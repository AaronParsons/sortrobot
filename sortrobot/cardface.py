import numpy as np
from scipy import ndimage
from skimage.measure import label, regionprops
from skimage.filters import rank
from skimage.transform import rotate
from skimage.segmentation import watershed, clear_border
from skimage.io import imread
from skimage.util import invert, img_as_ubyte
from skimage.morphology import disk, remove_small_objects

def _possibly_title(region):
    '''Determine if region could possibly be a title bar. Goal is to
    allow some false positives but no false negatives.'''
    # XXX currently hardcoded for (480,640) card images
    try:
        assert 75 < region.centroid[0] < 400 # roughly in top of img
        assert region.filled_area > 3750 # has substantial area
        assert 30 < region.minor_axis_length < 70 # thin
        assert np.pi > abs(region.orientation) > 1.52 # horizontal
        return True
    except(AssertionError):
        return False

def _merge_regions(regions, labels):
    '''Combine regions the watershed might have spuriously bisected.
    Checks if centroids of two regions fall inside the other's vertical 
    bounds.'''
    if len(regions) <= 1:
        return regions, labels
    # Get list of regions to merge based on compatible vertical bounds
    to_merge = []
    for i,r_i in enumerate(regions):
        xi1, _, xi2, _ = r_i.bbox
        for r_j in regions[i+1:]:
            xj1, _, xj2, _ = r_j.bbox
            if xj1 <= r_i.centroid[0] <= xj2 and \
                    xi1 <= r_j.centroid[0] <= xi2:
                to_merge.append((r_i,r_j))
    # Rewrite labels
    for r_i,r_j in to_merge:
        labels[labels == r_j.label] = r_i.label
    # Deduce regions from new labels
    regions = regionprops(labels)
    regions = [r for r in regions if _possibly_title(r)]
    # Commenting out sanity check which fails if merging regions
    # results in an incompatible region
    #assert len(new_regions) == len(regions) - len(to_merge)
    return regions, labels

def _select_best_region(regions, fill_thresh=0.9, verbose=False):
    '''Choose region most likely to be the titlebar. Prefers regions
    centered in the image and mostly filled in. If multiple regions are
    still viable, selects the bottom-most one.'''
    if len(regions) <= 1:
        return regions
    # Check if centered, but if not, don't bail yet
    centered = [r for r in regions if 290 < r.centroid[1] < 340]
    if len(centered) == 1:
        if verbose:
            print('    SELECT: center winnowed from {} to {}'.format(
                    len(regions), len(centered)))
        return centered
    # Select best-filled regions
    maxfill = max([r.solidity for r in regions])
    filled = [r for r in regions if r.solidity > fill_thresh * maxfill]
    if len(filled) == 1:
        if verbose:
            print('    SELECT: fill winnowed from {} to {}'.format(
                    len(regions), len(filled)))
        return filled
    # If multiple regions meet these criteria, select the bottom
    # (highest row) one
    regions = sorted(filled, key=lambda r: r.centroid[0])
    if verbose:
        print('    SELECT: ranking windows vertically:', 
                [r.centroid for r in regions])
    return regions[-1:]

def _crop_titlebar(image, region, max_shift=30, verbose=False):
    '''Extract title bar image from identified in region, 
    rotating to flat.'''
    if type(image) is str:
        img = imread(image, as_gray=True)
    else:
        img = image.copy()
    ang = 180/np.pi * region.orientation
    if ang < 0:
        ang += 180
    # Rotate title bar to flat
    img = rotate(img, 90 - ang, center=region.centroid[::-1])
    x1, y1, x2, y2 = region.bbox
    # override box width if unreasonable
    # XXX hardcoded pixel values
    default_y1 = 110
    default_y2 = 535
    if abs(y1 - default_y1) > max_shift:
        if verbose:
            print('    CROP: overriding y1={} with {}'.format(y1,
                                                              default_y1))
        y1 = default_y1
    if abs(y2 - default_y2) > max_shift:
        if verbose:
            print('    CROP: overriding y2={} with {}'.format(y2,
                                                              default_y2))
        y2 = default_y2
    title_bar = img[x1:x2,y1:y2]
    return title_bar


def extract_titlebar(image, min_brightness=0.3, ker_size=2, seed_thresh=20,
        min_seed_size=400, verbose=False):
    '''Extract the title bar from the image of a scanned (front, top face)
    card.'''
    if type(image) is str:
        img = imread(image, as_gray=True)
    else:
        img = image.copy()
    # Basic equalization
    img -= img.min()
    img /= img.max()
    mean = img.mean()
    if mean < 0.66 * min_brightness: # Dim card
        img = (min_brightness/mean * img).clip(0,1)
    # Prepare watershed procedure
    ker = disk(ker_size)
    img = rank.median(img_as_ubyte(img), ker) # despeckle
    grad = rank.gradient(img, ker) # find edges
    seeds = grad < seed_thresh # id low-gradient fields
    seeds = remove_small_objects(seeds, min_seed_size) # seed larger fields
    seeds = ndimage.label(seeds)[0] # mark pixels with labels
    labels = watershed(grad, seeds) # grow labels from seeds
    # Winnow watershed regions into title candidates
    labels = clear_border(labels) # toss out labels that hit image edge
    regions = [r for r in regionprops(labels) if _possibly_title(r)]
    regions, labels = _merge_regions(regions, labels)
    regions = _select_best_region(regions, verbose=verbose)

    assert len(regions) > 0 # We failed to find the title bar
        
    # With primary candidate selected, expand region horizontally 
    # using other identified regions to get a best estimate of
    # horizontal extent
    region = regions[0]
    x1, y1, x2, y2 = region.bbox
    # Identify horizontally adjacent regions
    adjacents = set(labels[x1:x2, y1-1:y2+1].flatten())
    adjacents.remove(region.label) # no self-ids
    try:
        adjacents.remove(0) # don't expand into unidentified/bg regions
    except(KeyError):
        pass
    # Annex horizontally adjacent regions
    for lbl in adjacents:
        labels[x1:x2][labels[x1:x2] == lbl] = region.label
    # Reconstitute our expanded region
    region = [r for r in regionprops(labels) if r.label == region.label][0]
    title_bar = _crop_titlebar(image, region, verbose=verbose)
    return title_bar
