import {
	getWindows,
	screen,
	Region,
	Image,
	mouse,
	Point,
} from "@nut-tree-fork/nut-js";
import * as path from "path";
import * as mouseService from "./mouseService";

export interface WindowInfo {
	title: string;
	x: number;
	y: number;
	width: number;
	height: number;
}

export class WindowService {
	private foundWindow: WindowInfo | null = null;
	private capturedImage: Image | null = null;

	/**
	 * Finds a window by its title (case-insensitive partial match) and stores it in memory
	 * @param title - The window title or partial title to search for
	 * @returns WindowInfo object with window position and dimensions, or null if not found
	 */
	async findWindowByTitle(title: string): Promise<WindowInfo | null> {
		try {
			const windows = await getWindows();

			// Find window with matching title (case-insensitive)
			for (const window of windows) {
				const windowTitle = await window.title;
				if (windowTitle.toLowerCase().includes(title.toLowerCase())) {
					const region = await window.region;

					this.foundWindow = {
						title: windowTitle,
						x: region.left,
						y: region.top,
						width: region.width,
						height: region.height,
					};

					return this.foundWindow;
				}
			}

			this.foundWindow = null;
			return null;
		} catch (error) {
			console.error("Error finding window:", error);
			this.foundWindow = null;
			return null;
		}
	}

	/**
	 * Gets the currently stored window info
	 * @returns The stored WindowInfo or null if no window has been found
	 */
	getStoredWindow(): WindowInfo | null {
		return this.foundWindow;
	}

	/**
	 * Captures a screenshot of the stored window and saves it to the project root
	 * @param filename - The filename for the screenshot (without extension)
	 * @returns The full path to the saved screenshot, or null if no window is stored
	 */
	async captureWindow(
		filename: string = "window-capture",
	): Promise<string | null> {
		if (!this.foundWindow) {
			console.error("No window stored. Call findWindowByTitle first.");
			return null;
		}

		try {
			const windowRegion = new Region(
				this.foundWindow.x,
				this.foundWindow.y,
				this.foundWindow.width,
				this.foundWindow.height,
			);

			const projectRoot = path.resolve(__dirname, "../..");
			const outputPath = await screen.captureRegion(
				filename,
				windowRegion,
				undefined,
				projectRoot,
			);

			console.log(`Screenshot saved to: ${outputPath}`);
			return outputPath;
		} catch (error) {
			console.error("Error capturing window:", error);
			return null;
		}
	}

	/**
	 * Captures a screenshot of the stored window and holds it in memory
	 * @returns The captured Image object, or null if no window is stored
	 */
	async captureWindowToMemory(): Promise<Image | null> {
		if (!this.foundWindow) {
			console.error("No window stored. Call findWindowByTitle first.");
			return null;
		}

		try {
			const windowRegion = new Region(
				this.foundWindow.x,
				this.foundWindow.y,
				this.foundWindow.width,
				this.foundWindow.height,
			);

			this.capturedImage = await screen.grabRegion(windowRegion);
			console.log(
				`Screenshot captured to memory: ${this.capturedImage.width}x${this.capturedImage.height}`,
			);
			return this.capturedImage;
		} catch (error) {
			console.error("Error capturing window to memory:", error);
			return null;
		}
	}

	/**
	 * Gets the currently stored image from memory
	 * @returns The stored Image or null if no image has been captured
	 */
	getCapturedImage(): Image | null {
		return this.capturedImage;
	}

	/**
	 * Moves the mouse to a position relative to the stored window's top-left corner
	 * @param relativeX - X coordinate relative to the window (0 = left edge)
	 * @param relativeY - Y coordinate relative to the window (0 = top edge)
	 * @returns True if successful, false if no window is stored or coordinates are out of bounds
	 */
	async moveMouseToWindowPosition(
		relativeX: number,
		relativeY: number,
	): Promise<boolean> {
		if (!this.foundWindow) {
			console.error("No window stored. Call findWindowByTitle first.");
			return false;
		}

		// Validate coordinates are within window bounds
		if (
			relativeX < 0 ||
			relativeX > this.foundWindow.width ||
			relativeY < 0 ||
			relativeY > this.foundWindow.height
		) {
			console.warn(
				`Coordinates (${relativeX}, ${relativeY}) are outside window bounds (${this.foundWindow.width}x${this.foundWindow.height})`,
			);
		}

		try {
			const absoluteX = this.foundWindow.x + relativeX;
			const absoluteY = this.foundWindow.y + relativeY;

			await mouseService.moveTo(absoluteX, absoluteY);
			console.log(
				`Mouse moved to window position (${relativeX}, ${relativeY}) -> screen position (${absoluteX}, ${absoluteY})`,
			);
			return true;
		} catch (error) {
			console.error("Error moving mouse:", error);
			return false;
		}
	}
}
