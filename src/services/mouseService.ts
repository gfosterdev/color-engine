import { mouse, Point, Button } from "@nut-tree-fork/nut-js";

/**
 * Bezier curve interpolation for smooth movement
 */
function bezierCurve(
	t: number,
	p0: number,
	p1: number,
	p2: number,
	p3: number,
): number {
	const u = 1 - t;
	const tt = t * t;
	const uu = u * u;
	const uuu = uu * u;
	const ttt = tt * t;

	return uuu * p0 + 3 * uu * t * p1 + 3 * u * tt * p2 + ttt * p3;
}

/**
 * Generate control points for bezier curve with slight randomness
 */
function generateControlPoints(
	start: Point,
	end: Point,
): { cp1: Point; cp2: Point } {
	const distance = Math.sqrt(
		Math.pow(end.x - start.x, 2) + Math.pow(end.y - start.y, 2),
	);

	// Add randomness to control points (30-70% of the distance)
	const spread = distance * (0.3 + Math.random() * 0.4);
	const angle1 = Math.random() * Math.PI * 2;
	const angle2 = Math.random() * Math.PI * 2;

	const cp1 = new Point(
		start.x + (end.x - start.x) * 0.25 + Math.cos(angle1) * spread * 0.3,
		start.y + (end.y - start.y) * 0.25 + Math.sin(angle1) * spread * 0.3,
	);

	const cp2 = new Point(
		start.x + (end.x - start.x) * 0.75 + Math.cos(angle2) * spread * 0.3,
		start.y + (end.y - start.y) * 0.75 + Math.sin(angle2) * spread * 0.3,
	);

	return { cp1, cp2 };
}

/**
 * Move mouse smoothly to absolute screen coordinates with human-like movement
 */
export async function moveTo(x: number, y: number): Promise<void> {
	const start = await mouse.getPosition();
	const end = new Point(x, y);

	const distance = Math.sqrt(
		Math.pow(end.x - start.x, 2) + Math.pow(end.y - start.y, 2),
	);

	// If distance is very small, just move directly
	if (distance < 5) {
		await mouse.setPosition(end);
		return;
	}

	// Generate bezier curve control points
	const { cp1, cp2 } = generateControlPoints(start, end);

	// Calculate number of steps based on distance (more steps for longer distances)
	const steps = Math.max(10, Math.min(100, Math.floor(distance / 5)));

	// Move along the bezier curve
	for (let i = 1; i <= steps; i++) {
		const t = i / steps;

		// Use ease-out function for more natural deceleration
		const easeT = 1 - Math.pow(1 - t, 3);

		const currentX = bezierCurve(easeT, start.x, cp1.x, cp2.x, end.x);
		const currentY = bezierCurve(easeT, start.y, cp1.y, cp2.y, end.y);

		await mouse.setPosition(
			new Point(Math.round(currentX), Math.round(currentY)),
		);

		// Add slight random delay between movements (1-5ms)
		await new Promise((resolve) =>
			setTimeout(resolve, 1 + Math.random() * 4),
		);
	}

	// Ensure we end exactly at the target
	await mouse.setPosition(end);
}

/**
 * Move mouse relative to current position
 */
export async function moveRelative(dx: number, dy: number): Promise<void> {
	const currentPos = await mouse.getPosition();
	await mouse.setPosition(new Point(currentPos.x + dx, currentPos.y + dy));
}

/**
 * Get current mouse position
 */
export async function getPosition(): Promise<Point> {
	return await mouse.getPosition();
}

/**
 * Click at current position
 */
export async function click(button: Button = Button.LEFT): Promise<void> {
	await mouse.click(button);
}

/**
 * Click at specific coordinates
 */
export async function clickAt(
	x: number,
	y: number,
	button: Button = Button.LEFT,
): Promise<void> {
	await moveTo(x, y);
	await mouse.click(button);
}

/**
 * Double click at current position
 */
export async function doubleClick(button: Button = Button.LEFT): Promise<void> {
	await mouse.doubleClick(button);
}

/**
 * Press and hold mouse button
 */
export async function pressButton(button: Button = Button.LEFT): Promise<void> {
	await mouse.pressButton(button);
}

/**
 * Release mouse button
 */
export async function releaseButton(
	button: Button = Button.LEFT,
): Promise<void> {
	await mouse.releaseButton(button);
}

/**
 * Drag from current position to target coordinates
 */
export async function drag(toX: number, toY: number): Promise<void> {
	await mouse.drag([new Point(toX, toY)]);
}

export default {
	moveTo,
	moveRelative,
	getPosition,
	click,
	clickAt,
	doubleClick,
	pressButton,
	releaseButton,
	drag,
};
