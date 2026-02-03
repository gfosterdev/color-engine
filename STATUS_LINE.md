# Status Line System

The skill bot base class now includes a persistent status line that displays real-time bot statistics in the terminal.

## Features

The status line:

- **Stays visible**: Uses carriage return (`\r`) to overwrite the same line in the terminal
- **Updates automatically**: Refreshes after each bot cycle
- **Customizable**: Child classes can override to show skill-specific information
- **Non-intrusive**: Doesn't clutter terminal output with repeated prints

## Base Implementation

In `SkillBotBase`, the status line shows:

- **State**: Current bot state (GATHERING, BANKING, WALKING, etc.)
- **Inventory**: Current capacity (X/28)
- **Gathered**: Total resources collected
- **Runtime**: Elapsed time in HH:MM:SS format

Example output:

```
State: GATHERING    | Inventory: 15/28 | Gathered:  142 | Runtime: 01:23:45
```

## Architecture

The status line system consists of three methods in `SkillBotBase`:

### 1. `_get_status_info() -> Dict`

Collects status information into a dictionary. Override this in child classes to add custom stats.

**Base implementation returns:**

```python
{
    'state': 'GATHERING',
    'inventory': '15/28',
    'resources': 142,
    'runtime': '01:23:45'
}
```

### 2. `_format_status_line(status_info: Dict) -> str`

Formats the status dictionary into a display string. Override to customize the layout.

**Base implementation:**

```python
f"State: {status_info['state']:12} | "
f"Inventory: {status_info['inventory']:5} | "
f"Gathered: {status_info['resources']:4} | "
f"Runtime: {status_info['runtime']}"
```

### 3. `_print_status_line()`

Prints the formatted status line using `\r` to overwrite the previous line. Usually doesn't need to be overridden.

## Customization in Child Classes

Child classes can override `_get_status_info()` and `_format_status_line()` to add skill-specific information.

### Woodcutting Bot Example

```python
def _get_status_info(self) -> Dict:
    """Override to add woodcutting-specific status information."""
    base_info = super()._get_status_info()

    # Update resources with logs count
    base_info['resources'] = self.logs_cut

    # Add woodcutting-specific info
    base_info['logs_cut'] = self.logs_cut
    base_info['banking_trips'] = self.banking_trips
    base_info['nests'] = self.nests_collected

    return base_info

def _format_status_line(self, status_info: Dict) -> str:
    """Override to format woodcutting-specific status line."""
    return (
        f"State: {status_info['state']:12} | "
        f"Inv: {status_info['inventory']:5} | "
        f"Logs: {status_info['logs_cut']:4} | "
        f"Banks: {status_info['banking_trips']:3} | "
        f"Nests: {status_info['nests']:2} | "
        f"Time: {status_info['runtime']}"
    )
```

Output:

```
State: GATHERING    | Inv: 15/28 | Logs:  142 | Banks:   5 | Nests:  2 | Time: 01:23:45
```

### Mining Bot Example

```python
def _get_status_info(self) -> Dict:
    """Override to add mining-specific status information."""
    base_info = super()._get_status_info()

    base_info['resources'] = self.ores_mined
    base_info['ores_mined'] = self.ores_mined
    base_info['banking_trips'] = self.banking_trips

    return base_info

def _format_status_line(self, status_info: Dict) -> str:
    """Override to format mining-specific status line."""
    return (
        f"State: {status_info['state']:12} | "
        f"Inv: {status_info['inventory']:5} | "
        f"Ores: {status_info['ores_mined']:4} | "
        f"Banks: {status_info['banking_trips']:3} | "
        f"Time: {status_info['runtime']}"
    )
```

Output:

```
State: GATHERING    | Inv: 22/28 | Ores:   87 | Banks:   3 | Time: 00:45:12
```

## Testing

Use `test_status_line.py` to test the status line functionality:

```bash
# Test woodcutting bot status line
python test_status_line.py woodcutting

# Test mining bot status line
python test_status_line.py mining
```

## Implementation Notes

1. **Carriage Return**: The `\r` character returns the cursor to the beginning of the line without creating a newline
2. **Flush Output**: `sys.stdout.flush()` ensures the status line is immediately visible
3. **Update Frequency**: Status line updates after each `_run_cycle()` completion
4. **Terminal Compatibility**: Works on Windows, Linux, and macOS terminals
5. **Debug Mode**: Status line works alongside debug prints - debug messages will push the status line down

## Best Practices

When overriding status methods:

1. **Always call `super()`**: Get base status info first, then add your custom fields
2. **Consistent formatting**: Use fixed-width fields with format specifications (e.g., `:12`, `:5`)
3. **Keep it concise**: Status line should fit in a standard terminal width (~80 chars)
4. **Update counters**: Make sure to increment your custom statistics in the gather methods
5. **Use clear labels**: Use short but descriptive labels (e.g., "Logs" not "L")

## Future Enhancements

Possible additions:

- XP/hour calculations
- Estimated time to level
- Profit tracking
- Resource value display
- Actions per minute (APM)
- Session efficiency metrics
