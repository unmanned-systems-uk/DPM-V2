Monitor PropertyLoader on Air-Side:

  # View PropertyLoader initialization logs
  docker logs payload-manager 2>&1 | grep -i property

  # Monitor all logs in real-time
  docker logs -f payload-manager

  # Monitor PropertyLoader with timestamps
  docker logs -f --timestamps payload-manager 2>&1 | grep -i property

  Monitor Camera Operations:

  # Watch camera property changes and validation
  docker logs -f payload-manager 2>&1 | grep -E "Setting property|Property set|Invalid.*value|PropertyLoader"

  # Monitor camera connection and property operations
  docker logs -f payload-manager 2>&1 | grep -E "Camera|PropertyLoader|Setting property"

  # Watch for validation errors
  docker logs -f payload-manager 2>&1 | grep -E "ERROR|Invalid.*value|not in specification"

  Complete View (Last 100 Lines):

  # See recent logs
  docker logs --tail 100 payload-manager

  # See recent logs with timestamps
  docker logs --tail 100 --timestamps payload-manager

  Recommended Command for Testing:

  # Monitor camera operations and property validation in real-time
  docker logs -f payload-manager 2>&1 | grep -E "PropertyLoader|Setting property|Property set|Invalid"

  Verify PropertyLoader is Working:

  # Check PropertyLoader initialization (should show 35/56/23 values)
  docker logs payload-manager 2>&1 | grep "PropertyLoader: Loaded"

  Expected output:
  PropertyLoader: Loaded 35 ISO values
  PropertyLoader: Loaded 56 shutter speed values
  PropertyLoader: Loaded 23 aperture values
  PropertyLoader: Initialization complete

  This will show you when Android sends property changes and whether they pass validation!