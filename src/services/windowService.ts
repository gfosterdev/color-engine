import { getWindows, getActiveWindow, Region } from "@nut-tree-fork/nut-js";

export interface WindowInfo {
	title: string;
	region: Region;
	x: number;
	y: number;
	width: number;
	height: number;
}

/**
 * Service for identifying and locating Windows applications
 */
class WindowService {
	/**
	 * Get all open windows
	 */
	async getAllWindows(): Promise<WindowInfo[]> {
		const windows = await getWindows();
		const windowInfos = await Promise.all(
			windows.map(async (win) => {
				const title = await win.title;
				const region = await win.region;
				// Calculate width/height from bounds if not provided
				const width =
					region.width ||
					((region as any).right
						? (region as any).right - region.left
						: 0);
				const height =
					region.height ||
					((region as any).bottom
						? (region as any).bottom - region.top
						: 0);
				return {
					title,
					region,
					x: region.left,
					y: region.top,
					width,
					height,
				};
			}),
		);
		return windowInfos;
	}

	/**
	 * Find a window by partial title match (case-insensitive)
	 */
	async findWindowByTitle(titlePattern: string): Promise<WindowInfo | null> {
		const windows = await this.getAllWindows();
		const pattern = titlePattern.toLowerCase();

		const match = windows.find((win) =>
			win.title.toLowerCase().includes(pattern),
		);

		return match || null;
	}

	/**
	 * Find all windows matching a title pattern
	 */
	async findWindowsByTitle(titlePattern: string): Promise<WindowInfo[]> {
		const windows = await this.getAllWindows();
		const pattern = titlePattern.toLowerCase();

		return windows.filter((win) =>
			win.title.toLowerCase().includes(pattern),
		);
	}

	/**
	 * Get the currently active (focused) window
	 */
	async getActiveWindow(): Promise<WindowInfo | null> {
		try {
			const activeWin = await getActiveWindow();
			const title = await activeWin.title;
			const region = await activeWin.region;
			// Calculate width/height from bounds if not provided
			const width =
				region.width ||
				((region as any).right
					? (region as any).right - region.left
					: 0);
			const height =
				region.height ||
				((region as any).bottom
					? (region as any).bottom - region.top
					: 0);
			return {
				title,
				region,
				x: region.left,
				y: region.top,
				width,
				height,
			};
		} catch (error) {
			console.error("Failed to get active window:", error);
			return null;
		}
	}

	/**
	 * Get the center point of a window (useful for clicking)
	 */
	getWindowCenter(windowInfo: WindowInfo): { x: number; y: number } {
		return {
			x: Math.floor(windowInfo.x + windowInfo.width / 2),
			y: Math.floor(windowInfo.y + windowInfo.height / 2),
		};
	}

	/**
	 * Convert relative coordinates (within window) to absolute screen coordinates
	 */
	relativeToAbsolute(
		windowInfo: WindowInfo,
		relativeX: number,
		relativeY: number,
	): { x: number; y: number } {
		return {
			x: windowInfo.x + relativeX,
			y: windowInfo.y + relativeY,
		};
	}

	/**
	 * Convert absolute screen coordinates to relative window coordinates
	 */
	absoluteToRelative(
		windowInfo: WindowInfo,
		absoluteX: number,
		absoluteY: number,
	): { x: number; y: number } {
		return {
			x: absoluteX - windowInfo.x,
			y: absoluteY - windowInfo.y,
		};
	}

	/**
	 * Check if a point (in absolute coordinates) is within a window
	 */
	isPointInWindow(windowInfo: WindowInfo, x: number, y: number): boolean {
		return (
			x >= windowInfo.x &&
			x <= windowInfo.x + windowInfo.width &&
			y >= windowInfo.y &&
			y <= windowInfo.y + windowInfo.height
		);
	}

	/**
	 * Get a random point within a window's bounds
	 */
	getRandomPointInWindow(
		windowInfo: WindowInfo,
		padding: number = 10,
	): { x: number; y: number } {
		const minX = windowInfo.x + padding;
		const maxX = windowInfo.x + windowInfo.width - padding;
		const minY = windowInfo.y + padding;
		const maxY = windowInfo.y + windowInfo.height - padding;

		return {
			x: Math.floor(Math.random() * (maxX - minX + 1)) + minX,
			y: Math.floor(Math.random() * (maxY - minY + 1)) + minY,
		};
	}
}

export default new WindowService();
