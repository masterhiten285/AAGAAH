"""Stage 6: metric DEM conditioning, D8 routing, accumulation and delineation."""
import heapq
import numpy as np

NEIGHBORS = [(r, c) for r in (-1, 0, 1) for c in (-1, 0, 1) if r or c]

def condition_dem(dem: np.ndarray) -> np.ndarray:
    if dem.ndim != 2 or not np.isfinite(dem).all():
        raise ValueError('DEM must be a finite two-dimensional metric-elevation raster')
    filled = dem.astype('float64').copy()
    height, width = dem.shape
    visited = np.zeros(dem.shape, dtype=bool)
    heap = []
    for r in range(height):
        for c in (0, width - 1):
            visited[r, c] = True
            heapq.heappush(heap, (filled[r, c], r, c))
    for c in range(1, width - 1):
        for r in (0, height - 1):
            visited[r, c] = True
            heapq.heappush(heap, (filled[r, c], r, c))
    while heap:
        z, r, c = heapq.heappop(heap)
        for dr, dc in NEIGHBORS:
            rr, cc = r + dr, c + dc
            if 0 <= rr < height and 0 <= cc < width and not visited[rr, cc]:
                visited[rr, cc] = True
                # Small deterministic gradient resolves flats without introducing cycles.
                filled[rr, cc] = max(filled[rr, cc], z + 0.00001)
                heapq.heappush(heap, (filled[rr, cc], rr, cc))
    return filled

def route_d8(filled: np.ndarray, cell_size: float):
    h, w = filled.shape
    ids = np.arange(h*w).reshape(h, w)
    receiver = np.full((h, w), -1, dtype=np.int64)
    best = np.zeros((h, w))
    for dr, dc in NEIGHBORS:
        r0, r1, c0, c1 = max(0,-dr), min(h,h-dr), max(0,-dc), min(w,w-dc)
        source = (slice(r0,r1),slice(c0,c1))
        target = (slice(r0+dr,r1+dr),slice(c0+dc,c1+dc))
        gradient = (filled[source] - filled[target]) / (cell_size * np.hypot(dr, dc))
        update = gradient > best[source]
        best[source][update] = gradient[update]
        receiver[source][update] = ids[target][update]
    order = np.argsort(filled.ravel())
    receiver = receiver.ravel()
    accumulation = np.ones(h*w, dtype=np.int64)
    for cell in order[::-1]:
        target = receiver[cell]
        if target >= 0: accumulation[target] += accumulation[cell]
    return receiver, accumulation.reshape(h,w), order

def delineate(receiver, order, outlets):
    """Assign each cell to its first downstream outlet (incremental subcatchments)."""
    labels = np.full(len(receiver), -1, dtype=np.int32)
    for label, outlet in enumerate(outlets): labels[outlet] = label
    outlet_set = set(outlets)
    for cell in order:
        if cell not in outlet_set and receiver[cell] >= 0:
            labels[cell] = labels[receiver[cell]]
    return labels
