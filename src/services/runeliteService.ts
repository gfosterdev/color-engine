import windowService, { WindowInfo } from "./windowService";
import mouseService from "./mouseService";

/**
 * Service for interacting with the RuneLite window
 * Provides convenience methods for mouse movement relative to the RuneLite window
 */
class RuneLiteService {
	private cachedWindow: WindowInfo | null = null;
	private cacheTimestamp: number = 0;
	private readonly CACHE_DURATION_MS = 5000; // Cache window info for 5 seconds

	/**
	 * Find and cache the RuneLite window
	 * @param titlePattern Optional custom title pattern (defaults to "RuneLite")
	 */
	async findWindow(
		titlePattern: string = "RuneLite",
	): Promise<WindowInfo | null> {
		const now = Date.now();

		// Return cached window if still valid
		if (
			this.cachedWindow &&
			now - this.cacheTimestamp < this.CACHE_DURATION_MS
		) {
			return this.cachedWindow;
		}

		// Find the window
		const window = await windowService.findWindowByTitle(titlePattern);

		if (window) {
			this.cachedWindow = window;
			this.cacheTimestamp = now;
		}

		return window;
	}

	/**
	 * Force refresh the cached window information
	 */
	async refreshWindow(
		titlePattern: string = "RuneLite",
	): Promise<WindowInfo | null> {
		this.cachedWindow = null;
		this.cacheTimestamp = 0;
		return this.findWindow(titlePattern);
	}

	/**
	 * Get the cached window info without refreshing
	 */
	getCachedWindow(): WindowInfo | null {
		const now = Date.now();
		if (
			this.cachedWindow &&
			now - this.cacheTimestamp < this.CACHE_DURATION_MS
		) {
			return this.cachedWindow;
		}
		return null;
	}

	/**
	 * Move mouse to a position relative to the RuneLite window's top-left corner
	 * @param relativeX X coordinate relative to window (0 = left edge)
	 * @param relativeY Y coordinate relative to window (0 = top edge)
	 */
	async moveToRelative(relativeX: number, relativeY: number): Promise<void> {
		const window = await this.findWindow();
		if (!window) {
			throw new Error("RuneLite window not found");
		}

		const absolutePos = windowService.relativeToAbsolute(
			window,
			relativeX,
			relativeY,
		);
		await mouseService.moveTo(absolutePos.x, absolutePos.y);
	}

	/**
	 * Move mouse to the center of the RuneLite window
	 */
	async moveToCenter(): Promise<void> {
		const window = await this.findWindow();
		if (!window) {
			throw new Error("RuneLite window not found");
		}

		const center = windowService.getWindowCenter(window);
		await mouseService.moveTo(center.x, center.y);
	}

	/**
	 * Move mouse to a random position within the RuneLite window
	 * @param padding Padding from window edges in pixels (default: 10)
	 */
	async moveToRandomPosition(padding: number = 10): Promise<void> {
		const window = await this.findWindow();
		if (!window) {
			throw new Error("RuneLite window not found");
		}

		const randomPos = windowService.getRandomPointInWindow(window, padding);
		await mouseService.moveTo(randomPos.x, randomPos.y);
	}

	/**
	 * Move mouse to a relative position with percentage-based coordinates
	 * @param percentX X position as percentage of window width (0-100)
	 * @param percentY Y position as percentage of window height (0-100)
	 */
	async moveToPercent(percentX: number, percentY: number): Promise<void> {
		const window = await this.findWindow();
		if (!window) {
			throw new Error("RuneLite window not found");
		}

		const relativeX = (percentX / 100) * window.width;
		const relativeY = (percentY / 100) * window.height;

		const absolutePos = windowService.relativeToAbsolute(
			window,
			relativeX,
			relativeY,
		);
		await mouseService.moveTo(absolutePos.x, absolutePos.y);
	}

	/**
	 * Click at a position relative to the RuneLite window
	 * @param relativeX X coordinate relative to window
	 * @param relativeY Y coordinate relative to window
	 */
	async clickRelative(relativeX: number, relativeY: number): Promise<void> {
		await this.moveToRelative(relativeX, relativeY);
		await mouseService.click();
	}

	/**
	 * Right-click at a position relative to the RuneLite window
	 * @param relativeX X coordinate relative to window
	 * @param relativeY Y coordinate relative to window
	 */
	async rightClickRelative(
		relativeX: number,
		relativeY: number,
	): Promise<void> {
		await this.moveToRelative(relativeX, relativeY);
		await mouseService.rightClick();
	}

	/**
	 * Check if the mouse is currently within the RuneLite window bounds
	 */
	async isMouseInWindow(): Promise<boolean> {
		const window = await this.findWindow();
		if (!window) {
			return false;
		}

		const mousePos = await mouseService.getPosition();
		return windowService.isPointInWindow(window, mousePos.x, mousePos.y);
	}

	/**
	 * Get the current mouse position relative to the RuneLite window
	 * Returns null if window is not found
	 */
	async getRelativeMousePosition(): Promise<{ x: number; y: number } | null> {
		const window = await this.findWindow();
		if (!window) {
			return null;
		}

		const mousePos = await mouseService.getPosition();
		return windowService.absoluteToRelative(window, mousePos.x, mousePos.y);
	}

	/**
	 * Get the RuneLite window dimensions
	 */
	async getWindowDimensions(): Promise<{
		width: number;
		height: number;
	} | null> {
		const window = await this.findWindow();
		if (!window) {
			return null;
		}

		return {
			width: window.width,
			height: window.height,
		};
	}

	/**
	 * Get the RuneLite window position on screen
	 */
	async getWindowPosition(): Promise<{ x: number; y: number } | null> {
		const window = await this.findWindow();
		if (!window) {
			return null;
		}

		return {
			x: window.x,
			y: window.y,
		};
	}
}

export default new RuneLiteService();
