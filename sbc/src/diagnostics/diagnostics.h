#pragma once

#include <string>
#include "camera/camera_interface.h"

namespace Diagnostics {

/**
 * Run ISO sensitivity diagnostic
 * Queries camera for ISO property details and compares with specification
 * Returns: 0 on success, non-zero on failure
 */
int runISODiagnostic();

/**
 * Run exposure mode diagnostic
 * Queries camera shooting mode (M/A/S/P) and related properties
 * Returns: 0 on success, non-zero on failure
 */
int runExposureModeDiagnostic();

/**
 * List all camera properties
 * Dumps all available camera properties with current values
 * Returns: 0 on success, non-zero on failure
 */
int runPropertiesListDiagnostic();

/**
 * Run property mapping test
 * Tests conversion between human-readable and SDK values
 * Returns: 0 on success, non-zero on failure
 */
int runPropertyMappingDiagnostic();

/**
 * Parse and execute diagnostic command
 * Returns: 0 on success, non-zero on failure, -1 if not a diagnostic command
 */
int parseDiagnosticCommand(int argc, char* argv[]);

} // namespace Diagnostics
