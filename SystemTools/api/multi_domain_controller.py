"""
Multi-Domain Controller
=======================

High-level orchestration for coordinated operations across Air-Side,
Ground-Side, and SystemTools domains.

Provides:
- End-to-end test workflows
- Cross-domain synchronization
- Integration test framework
- Coordinated operations
- Multi-domain verification
"""

import time
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

from utils.protocol_logger import logger
from .response import APIResponse


class MultiDomainController:
    """
    Multi-Domain orchestration controller

    Coordinates operations across Air-Side, Ground-Side, and SystemTools
    for complex workflows and integration testing.

    Example:
        dpm = DPMController()

        # Run end-to-end workflow
        result = dpm.multi_domain.run_capture_workflow(
            quality=95,
            verify_logs=True,
            verify_ground_side=True
        )

        if result.success:
            print(f"Workflow completed: {result.data['steps_completed']}")
    """

    def __init__(self, air_side_controller, ground_side_controller, system_controller):
        """
        Initialize Multi-Domain controller

        Args:
            air_side_controller: AirSideController instance
            ground_side_controller: GroundSideController instance
            system_controller: SystemController instance
        """
        self.air_side = air_side_controller
        self.ground_side = ground_side_controller
        self.system = system_controller

        logger.debug("SYSTEM", "MultiDomainController initialized")

    def run_capture_workflow(
        self,
        quality: int = 95,
        verify_logs: bool = True,
        verify_ground_side: bool = False,
        capture_screenshot: bool = False
    ) -> APIResponse:
        """
        Run end-to-end image capture workflow

        Workflow:
        1. Connect to Air-Side
        2. Send camera.capture command
        3. Verify command in logs (if verify_logs=True)
        4. Verify Ground-Side app status (if verify_ground_side=True)
        5. Capture H16 screenshot (if capture_screenshot=True)
        6. Collect results and diagnostics

        Args:
            quality: JPEG quality (0-100)
            verify_logs: Verify capture command in SystemTools logs
            verify_ground_side: Check Ground-Side app status
            capture_screenshot: Capture H16 screenshot as evidence

        Returns:
            APIResponse with workflow results
        """
        try:
            workflow_start = time.time()
            steps = []

            # Step 1: Connect to Air-Side
            logger.info("SYSTEM", "Workflow: Connecting to Air-Side")
            air_connect = self.air_side.connect()
            steps.append({
                'step': 'connect_air_side',
                'success': air_connect.success,
                'duration_ms': 0
            })

            if not air_connect.success:
                return APIResponse.error_response(
                    error="Failed to connect to Air-Side",
                    domain="multi-domain",
                    operation="run_capture_workflow",
                    data={'steps': steps}
                )

            # Step 2: Send capture command
            logger.info("CAMERA", "Workflow: Sending camera.capture command")
            step_start = time.time()
            capture_result = self.air_side.send_command(
                'camera.capture',
                {'quality': quality}
            )
            steps.append({
                'step': 'camera_capture',
                'success': capture_result.success,
                'duration_ms': int((time.time() - step_start) * 1000)
            })

            # Step 3: Verify in logs
            if verify_logs:
                logger.info("SYSTEM", "Workflow: Verifying command in logs")
                step_start = time.time()
                time.sleep(0.5)  # Allow time for log propagation

                log_result = self.system.query_logs(
                    message_filter='camera.capture',
                    limit=10
                )

                log_verified = log_result.success and log_result.data['count'] > 0
                steps.append({
                    'step': 'verify_logs',
                    'success': log_verified,
                    'duration_ms': int((time.time() - step_start) * 1000),
                    'logs_found': log_result.data['count'] if log_result.success else 0
                })

            # Step 4: Verify Ground-Side
            if verify_ground_side:
                logger.info("SYSTEM", "Workflow: Checking Ground-Side status")
                step_start = time.time()

                ground_connect = self.ground_side.connect()
                if ground_connect.success:
                    diag_result = self.ground_side.get_diagnostics()
                    steps.append({
                        'step': 'ground_side_diagnostics',
                        'success': diag_result.success,
                        'duration_ms': int((time.time() - step_start) * 1000),
                        'diagnostics': diag_result.data if diag_result.success else None
                    })
                    self.ground_side.disconnect()
                else:
                    steps.append({
                        'step': 'ground_side_diagnostics',
                        'success': False,
                        'duration_ms': int((time.time() - step_start) * 1000),
                        'error': 'Failed to connect to Ground-Side'
                    })

            # Step 5: Capture screenshot
            if capture_screenshot and verify_ground_side:
                logger.info("CAMERA", "Workflow: Capturing H16 screenshot")
                step_start = time.time()

                if self.ground_side.is_connected() or self.ground_side.connect().success:
                    screenshot_path = f'/tmp/workflow_screenshot_{int(time.time())}.png'
                    screenshot_result = self.ground_side.get_screen_capture(screenshot_path)
                    steps.append({
                        'step': 'capture_screenshot',
                        'success': screenshot_result.success,
                        'duration_ms': int((time.time() - step_start) * 1000),
                        'path': screenshot_path if screenshot_result.success else None
                    })
                    self.ground_side.disconnect()

            # Disconnect Air-Side
            self.air_side.disconnect()

            # Calculate total duration
            workflow_duration = int((time.time() - workflow_start) * 1000)

            # Determine overall success
            all_success = all(step['success'] for step in steps)

            logger.info("SYSTEM", f"Workflow completed: {all_success} ({workflow_duration}ms)")

            return APIResponse.success_response(
                data={
                    'workflow': 'camera_capture',
                    'overall_success': all_success,
                    'steps': steps,
                    'steps_completed': len(steps),
                    'total_duration_ms': workflow_duration,
                    'timestamp': datetime.now().isoformat()
                },
                domain="multi-domain",
                operation="run_capture_workflow"
            )

        except Exception as e:
            logger.error("SYSTEM", f"Workflow error: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="multi-domain",
                operation="run_capture_workflow"
            )

    def run_health_check_workflow(self, include_ground_side: bool = True) -> APIResponse:
        """
        Run comprehensive health check across all domains

        Checks:
        - Air-Side connectivity and status
        - Ground-Side connectivity and diagnostics (optional)
        - SystemTools log queue and data storage

        Args:
            include_ground_side: Include Ground-Side in health check

        Returns:
            APIResponse with health status for all domains
        """
        try:
            health_results = {}

            # Air-Side health
            logger.info("HEALTH", "Health check: Air-Side")
            air_connect = self.air_side.connect()
            if air_connect.success:
                air_status = self.air_side.get_status()
                health_results['air_side'] = {
                    'connected': True,
                    'status': air_status.data if air_status.success else None,
                    'healthy': air_status.success
                }
                self.air_side.disconnect()
            else:
                health_results['air_side'] = {
                    'connected': False,
                    'healthy': False,
                    'error': air_connect.error
                }

            # Ground-Side health
            if include_ground_side:
                logger.info("HEALTH", "Health check: Ground-Side")
                ground_connect = self.ground_side.connect()
                if ground_connect.success:
                    ground_diag = self.ground_side.get_diagnostics()
                    health_results['ground_side'] = {
                        'connected': True,
                        'diagnostics': ground_diag.data if ground_diag.success else None,
                        'healthy': ground_diag.success
                    }
                    self.ground_side.disconnect()
                else:
                    health_results['ground_side'] = {
                        'connected': False,
                        'healthy': False,
                        'error': ground_connect.error
                    }

            # SystemTools health
            logger.info("HEALTH", "Health check: SystemTools")
            system_status = self.system.get_system_status()
            health_results['system_tools'] = {
                'healthy': system_status.success,
                'status': system_status.data if system_status.success else None
            }

            # Overall health
            all_healthy = all(
                domain.get('healthy', False)
                for domain in health_results.values()
            )

            logger.info("HEALTH", f"Overall health: {all_healthy}")

            return APIResponse.success_response(
                data={
                    'overall_healthy': all_healthy,
                    'domains': health_results,
                    'timestamp': datetime.now().isoformat()
                },
                domain="multi-domain",
                operation="run_health_check_workflow"
            )

        except Exception as e:
            logger.error("HEALTH", f"Health check error: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="multi-domain",
                operation="run_health_check_workflow"
            )

    def run_integration_test(
        self,
        test_name: str,
        test_steps: List[Dict[str, Any]],
        verify_each_step: bool = True
    ) -> APIResponse:
        """
        Run custom integration test across domains

        Args:
            test_name: Test identifier
            test_steps: List of test step definitions
                Each step: {
                    'domain': 'air_side' | 'ground_side' | 'system',
                    'operation': 'method_name',
                    'params': {},
                    'verify': bool
                }
            verify_each_step: Verify each step in logs before proceeding

        Returns:
            APIResponse with test results
        """
        try:
            logger.info("SYSTEM", f"Integration test: {test_name}")

            test_results = []
            start_time = time.time()

            for idx, step in enumerate(test_steps):
                step_start = time.time()
                domain = step.get('domain')
                operation = step.get('operation')
                params = step.get('params', {})

                logger.info("SYSTEM", f"Test step {idx+1}: {domain}.{operation}")

                # Execute step
                controller = getattr(self, domain, None)
                if not controller:
                    test_results.append({
                        'step': idx + 1,
                        'domain': domain,
                        'operation': operation,
                        'success': False,
                        'error': f"Unknown domain: {domain}"
                    })
                    continue

                method = getattr(controller, operation, None)
                if not method:
                    test_results.append({
                        'step': idx + 1,
                        'domain': domain,
                        'operation': operation,
                        'success': False,
                        'error': f"Unknown operation: {operation}"
                    })
                    continue

                result = method(**params)
                step_duration = int((time.time() - step_start) * 1000)

                test_results.append({
                    'step': idx + 1,
                    'domain': domain,
                    'operation': operation,
                    'success': result.success,
                    'duration_ms': step_duration,
                    'data': result.data if result.success else None,
                    'error': result.error if not result.success else None
                })

                # Verify in logs if requested
                if verify_each_step and step.get('verify', False):
                    time.sleep(0.3)  # Allow log propagation
                    log_result = self.system.query_logs(
                        message_filter=operation,
                        limit=5
                    )
                    test_results[-1]['log_verified'] = log_result.success and log_result.data['count'] > 0

            # Calculate results
            total_duration = int((time.time() - start_time) * 1000)
            passed = sum(1 for r in test_results if r['success'])
            total = len(test_results)

            logger.info("SYSTEM", f"Integration test complete: {passed}/{total} passed")

            return APIResponse.success_response(
                data={
                    'test_name': test_name,
                    'passed': passed,
                    'total': total,
                    'success_rate': (passed / total * 100) if total > 0 else 0,
                    'steps': test_results,
                    'total_duration_ms': total_duration,
                    'timestamp': datetime.now().isoformat()
                },
                domain="multi-domain",
                operation="run_integration_test"
            )

        except Exception as e:
            logger.error("SYSTEM", f"Integration test error: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="multi-domain",
                operation="run_integration_test"
            )

    def coordinate_air_ground_operation(
        self,
        air_side_command: str,
        air_side_params: Dict[str, Any],
        ground_side_action: str,
        ground_side_params: Dict[str, Any],
        verify_synchronization: bool = True
    ) -> APIResponse:
        """
        Coordinate synchronized operation between Air-Side and Ground-Side

        Example: Trigger capture on Air-Side and verify on Ground-Side app

        Args:
            air_side_command: Command to send to Air-Side
            air_side_params: Command parameters
            ground_side_action: Action to perform on Ground-Side
            ground_side_params: Action parameters
            verify_synchronization: Verify both operations in logs

        Returns:
            APIResponse with coordination results
        """
        try:
            logger.info("SYNC", f"Coordinating: {air_side_command} <-> {ground_side_action}")

            # Connect both domains
            air_result = self.air_side.connect()
            ground_result = self.ground_side.connect()

            if not (air_result.success and ground_result.success):
                return APIResponse.error_response(
                    error="Failed to connect to required domains",
                    domain="multi-domain",
                    operation="coordinate_air_ground_operation",
                    data={
                        'air_side_connected': air_result.success,
                        'ground_side_connected': ground_result.success
                    }
                )

            # Execute Air-Side operation
            air_start = time.time()
            air_op_result = self.air_side.send_command(air_side_command, air_side_params)
            air_duration = int((time.time() - air_start) * 1000)

            # Execute Ground-Side operation
            ground_start = time.time()
            ground_method = getattr(self.ground_side, ground_side_action, None)
            if ground_method:
                ground_op_result = ground_method(**ground_side_params)
            else:
                ground_op_result = APIResponse.error_response(
                    error=f"Unknown Ground-Side action: {ground_side_action}",
                    domain="ground-side",
                    operation=ground_side_action
                )
            ground_duration = int((time.time() - ground_start) * 1000)

            # Verify synchronization
            sync_verified = False
            if verify_synchronization:
                time.sleep(0.5)
                air_logs = self.system.query_logs(message_filter=air_side_command, limit=5)
                ground_logs = self.system.query_logs(message_filter=ground_side_action, limit=5)
                sync_verified = (
                    air_logs.success and air_logs.data['count'] > 0 and
                    ground_logs.success and ground_logs.data['count'] > 0
                )

            # Disconnect
            self.air_side.disconnect()
            self.ground_side.disconnect()

            operation_success = air_op_result.success and ground_op_result.success

            logger.info("SYNC", f"Coordination complete: {operation_success}")

            return APIResponse.success_response(
                data={
                    'synchronized': operation_success,
                    'sync_verified_in_logs': sync_verified,
                    'air_side': {
                        'command': air_side_command,
                        'success': air_op_result.success,
                        'duration_ms': air_duration
                    },
                    'ground_side': {
                        'action': ground_side_action,
                        'success': ground_op_result.success,
                        'duration_ms': ground_duration
                    },
                    'timestamp': datetime.now().isoformat()
                },
                domain="multi-domain",
                operation="coordinate_air_ground_operation"
            )

        except Exception as e:
            logger.error("SYNC", f"Coordination error: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="multi-domain",
                operation="coordinate_air_ground_operation"
            )

    def export_test_results(
        self,
        test_results: List[Dict[str, Any]],
        output_path: str,
        include_logs: bool = True,
        include_analytics: bool = True
    ) -> APIResponse:
        """
        Export comprehensive test results with logs and analytics

        Args:
            test_results: List of test result dictionaries
            output_path: Path to export file
            include_logs: Include relevant logs in export
            include_analytics: Include performance analytics

        Returns:
            APIResponse with export status
        """
        try:
            logger.info("STORAGE", f"Exporting test results to {output_path}")

            export_data = {
                'test_results': test_results,
                'export_timestamp': datetime.now().isoformat()
            }

            # Include logs
            if include_logs:
                recent_logs = self.system.query_logs(limit=500)
                if recent_logs.success:
                    export_data['logs'] = recent_logs.data['logs']

            # Include analytics
            if include_analytics:
                analytics = self.system.get_analytics()
                if analytics.success:
                    export_data['analytics'] = analytics.data

            # Export to file
            import json
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            logger.info("STORAGE", f"Test results exported: {output_path}")

            return APIResponse.success_response(
                data={
                    'output_path': output_path,
                    'test_count': len(test_results),
                    'log_count': len(export_data.get('logs', [])),
                    'includes_analytics': include_analytics
                },
                domain="multi-domain",
                operation="export_test_results"
            )

        except Exception as e:
            logger.error("STORAGE", f"Export error: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="multi-domain",
                operation="export_test_results"
            )
