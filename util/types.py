from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional, Tuple
import random
from .window_util import Region


Point = Tuple[int, int]


@dataclass(init=False)
class Polygon:
	points: List[Point] = field(default_factory=list)

	def __init__(self, points: Optional[Iterable[object]] = None) -> None:
		self.points = []
		if not points:
			return
		for p in points:
			if isinstance(p, dict):
				if 'x' not in p or 'y' not in p:
					raise TypeError(f"Point dict must contain 'x' and 'y': {p!r}")
				x = int(p['x'])
				y = int(p['y'])
				self.points.append((x, y))
			elif isinstance(p, (list, tuple)) and len(p) >= 2:
				self.points.append((int(p[0]), int(p[1])))
			else:
				# try attribute access (.x, .y)
				x = getattr(p, 'x', None)
				y = getattr(p, 'y', None)
				if x is not None and y is not None:
					self.points.append((int(x), int(y)))
				else:
					raise TypeError(f"Unsupported point format: {p!r}")

	def add_point(self, x: int, y: int) -> None:
		self.points.append((x, y))

	def extend(self, pts: Iterable[Point]) -> None:
		self.points.extend(pts)

	def __len__(self) -> int:
		return len(self.points)

	def __iter__(self) -> Iterator[Point]:
		return iter(self.points)

	def to_list(self) -> List[Point]:
		return list(self.points)

	def bounding_box(self) -> Optional[Tuple[int, int, int, int]]:
		if not self.points:
			return None
		xs = [p[0] for p in self.points]
		ys = [p[1] for p in self.points]
		return min(xs), min(ys), max(xs), max(ys)

	def area(self) -> float:
		if len(self.points) < 3:
			return 0.0
		a = 0.0
		pts = self.points
		n = len(pts)
		for i in range(n):
			x1, y1 = pts[i]
			x2, y2 = pts[(i + 1) % n]
			a += x1 * y2 - x2 * y1
		return abs(a) / 2.0

	def centroid(self) -> Optional[Tuple[float, float]]:
		if len(self.points) < 3:
			return None
		cx = 0.0
		cy = 0.0
		a = 0.0
		pts = self.points
		n = len(pts)
		for i in range(n):
			x0, y0 = pts[i]
			x1, y1 = pts[(i + 1) % n]
			cross = x0 * y1 - x1 * y0
			a += cross
			cx += (x0 + x1) * cross
			cy += (y0 + y1) * cross
		a *= 0.5
		if a == 0.0:
			return None
		cx /= (6.0 * a)
		cy /= (6.0 * a)
		return cx, cy

	def contains_point(self, x: int, y: int) -> bool:
		inside = False
		pts = self.points
		n = len(pts)
		if n == 0:
			return False
		j = n - 1
		for i in range(n):
			xi, yi = pts[i]
			xj, yj = pts[j]
			if (yi > y) != (yj > y):
				# compute intersection x coordinate of edge with horizontal line at y
				denom = (yj - yi)
				if denom == 0:
					x_intersect = xi
				else:
					x_intersect = (xj - xi) * (y - yi) / denom + xi
				if x < x_intersect:
					inside = not inside
			j = i
		return inside

	def __repr__(self) -> str:  # pragma: no cover - trivial
		return f"Polygon(points={self.points})"

	def random_point_inside(self, bounds: Optional[Region] = None) -> Tuple[int, int]:
		"""Return a random point inside the polygon.

		Uses a fan triangulation from the first vertex and samples a triangle
		with probability proportional to its area; then samples a point
		uniformly inside that triangle via barycentric coordinates.
		"""
		if len(self.points) < 3:
			raise ValueError("Polygon must have at least 3 points")

		p0 = self.points[0]
		triangles: List[Tuple[Point, Point, Point]] = []
		areas: List[float] = []
		# If bounds is provided, vertices outside bounds are clamped to the
		# closest point on the region (edge or corner).
		def _clamp(pt: Point) -> Point:
			if bounds is None:
				return pt
			bx = bounds.x
			by = bounds.y
			bw = bounds.width
			bh = bounds.height
			cx = min(max(pt[0], bx), bx + bw - 1)
			cy = min(max(pt[1], by), by + bh - 1)
			return (cx, cy)

		for i in range(1, len(self.points) - 1):
			raw_a = p0
			raw_b = self.points[i]
			raw_c = self.points[i + 1]
			a = _clamp(raw_a)
			b = _clamp(raw_b)
			c = _clamp(raw_c)
			cross = abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2.0
			triangles.append((a, b, c))
			areas.append(cross)

		total = sum(areas)
		if total == 0:
			raise ValueError("Polygon area is zero")

		# pick triangle weighted by area
		r = random.random() * total
		cum = 0.0
		chosen: Tuple[Point, Point, Point] = triangles[-1]
		for tri, area in zip(triangles, areas):
			cum += area
			if r <= cum:
				chosen = tri
				break

		# Try sampling until the point falls within bounds (if provided).
		max_attempts = 1000
		for _ in range(max_attempts):
			A, B, C = chosen
			r1 = random.random()
			r2 = random.random()
			if r1 + r2 > 1:
				r1 = 1 - r1
				r2 = 1 - r2

			x = A[0] + r1 * (B[0] - A[0]) + r2 * (C[0] - A[0])
			y = A[1] + r1 * (B[1] - A[1]) + r2 * (C[1] - A[1])
			xi, yi = int(round(x)), int(round(y))

			if bounds is None:
				return xi, yi

			# bounds is expected to be a Region; use its API directly.
			if bounds.contains(xi, yi):
				return xi, yi

		raise ValueError("Could not sample a point inside polygon that also lies within bounds")

