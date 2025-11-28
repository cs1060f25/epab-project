#!/usr/bin/env python3
"""
Test Runner Script for Cybersecurity & Fraud Detection Platform API
Orchestrates running different test suites and generates comprehensive reports
"""

import sys
import subprocess
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any
import json


class TestRunner:
    """Main test runner class"""
    
    def __init__(self, args):
        self.args = args
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_basic_tests(self) -> bool:
        """Run the basic API test suite"""
        print("🔍 Running Basic API Tests...")
        print("-" * 40)
        
        try:
            result = subprocess.run([
                sys.executable, "test_api.py"
            ], capture_output=True, text=True, timeout=300)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            self.results['basic_tests'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            return success
            
        except subprocess.TimeoutExpired:
            print("❌ Basic tests timed out")
            return False
        except Exception as e:
            print(f"❌ Error running basic tests: {e}")
            return False
    
    def run_comprehensive_tests(self) -> bool:
        """Run the comprehensive test suite"""
        print("🔍 Running Comprehensive API Tests...")
        print("-" * 40)
        
        try:
            result = subprocess.run([
                sys.executable, "test_comprehensive.py"
            ], capture_output=True, text=True, timeout=600)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            self.results['comprehensive_tests'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            return success
            
        except subprocess.TimeoutExpired:
            print("❌ Comprehensive tests timed out")
            return False
        except Exception as e:
            print(f"❌ Error running comprehensive tests: {e}")
            return False
    
    def run_pytest_suite(self) -> bool:
        """Run pytest-based test suite"""
        print("🔍 Running Pytest Test Suite...")
        print("-" * 40)
        
        try:
            pytest_args = [
                sys.executable, "-m", "pytest", 
                "test_pytest.py",
                "-v",
                "--tb=short"
            ]
            
            if self.args.coverage:
                pytest_args.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
            
            if self.args.markers:
                pytest_args.extend(["-m", self.args.markers])
            
            result = subprocess.run(pytest_args, capture_output=True, text=True, timeout=600)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            self.results['pytest_suite'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            return success
            
        except subprocess.TimeoutExpired:
            print("❌ Pytest suite timed out")
            return False
        except Exception as e:
            print(f"❌ Error running pytest suite: {e}")
            return False
    
    def run_security_tests(self) -> bool:
        """Run security-focused test suite"""
        print("🔒 Running Security Test Suite...")
        print("-" * 40)
        
        try:
            result = subprocess.run([
                sys.executable, "test_security.py"
            ], capture_output=True, text=True, timeout=600)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            self.results['security_tests'] = {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr
            }
            return success
            
        except subprocess.TimeoutExpired:
            print("❌ Security tests timed out")
            return False
        except Exception as e:
            print(f"❌ Error running security tests: {e}")
            return False
    
    def check_server_availability(self) -> bool:
        """Check if the API server is running"""
        print("🌐 Checking API Server Availability...")
        
        import requests
        try:
            response = requests.get("http://localhost:8000/docs", timeout=5)
            if response.status_code == 200:
                print("✅ API server is running and accessible")
                return True
            else:
                print(f"❌ API server returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to API server: {e}")
            print("💡 Make sure the API server is running on port 8000")
            return False
    
    def install_test_dependencies(self) -> bool:
        """Install test dependencies if needed"""
        if not self.args.install_deps:
            return True
        
        print("📦 Installing test dependencies...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Test dependencies installed successfully")
                return True
            else:
                print(f"❌ Failed to install dependencies: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    
    def generate_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_suites = len(self.results)
        passed_suites = sum(1 for r in self.results.values() if r['success'])
        
        print(f"Test Duration: {self.end_time - self.start_time:.2f} seconds")
        print(f"Test Suites Run: {total_suites}")
        print(f"✅ Passed: {passed_suites}")
        print(f"❌ Failed: {total_suites - passed_suites}")
        print(f"Success Rate: {(passed_suites/total_suites)*100:.1f}%")
        
        print("\n📋 Suite Results:")
        print("-" * 30)
        
        suite_names = {
            'basic_tests': 'Basic API Tests',
            'comprehensive_tests': 'Comprehensive Tests',
            'pytest_suite': 'Pytest Suite',
            'security_tests': 'Security Tests'
        }
        
        for suite_key, result in self.results.items():
            suite_name = suite_names.get(suite_key, suite_key)
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{suite_name:.<30} {status}")
        
        if self.args.save_report:
            self.save_json_report()
        
        # Overall assessment
        print("\n🎯 Overall Assessment:")
        if passed_suites == total_suites:
            print("🎉 All test suites passed! The API is functioning correctly.")
        elif passed_suites >= total_suites * 0.75:
            print("⚠️  Most tests passed, but some issues were found. Review failed tests.")
        else:
            print("🚨 Multiple test failures detected. API may have significant issues.")
    
    def save_json_report(self):
        """Save detailed test results as JSON"""
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': self.end_time - self.start_time,
            'total_suites': len(self.results),
            'passed_suites': sum(1 for r in self.results.values() if r['success']),
            'results': self.results
        }
        
        report_file = f"test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Detailed report saved to: {report_file}")
    
    def run_all_tests(self) -> bool:
        """Run all test suites"""
        self.start_time = time.time()
        
        print("🚀 Starting Comprehensive API Test Run")
        print("=" * 60)
        
        # Check prerequisites
        if not self.install_test_dependencies():
            return False
        
        if not self.check_server_availability():
            if not self.args.skip_server_check:
                return False
        
        # Run test suites based on arguments
        all_passed = True
        
        if self.args.basic or self.args.all:
            all_passed &= self.run_basic_tests()
            print()
        
        if self.args.comprehensive or self.args.all:
            all_passed &= self.run_comprehensive_tests()
            print()
        
        if self.args.pytest or self.args.all:
            all_passed &= self.run_pytest_suite()
            print()
        
        if self.args.security or self.args.all:
            all_passed &= self.run_security_tests()
            print()
        
        self.end_time = time.time()
        self.generate_report()
        
        return all_passed


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Comprehensive Test Runner for Cybersecurity API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                    # Run all test suites
  python run_tests.py --basic --comprehensive  # Run specific suites
  python run_tests.py --pytest --coverage      # Run pytest with coverage
  python run_tests.py --security               # Run only security tests
  python run_tests.py --all --save-report      # Run all and save JSON report
        """
    )
    
    # Test suite selection
    parser.add_argument('--all', action='store_true', 
                       help='Run all test suites')
    parser.add_argument('--basic', action='store_true',
                       help='Run basic API tests')
    parser.add_argument('--comprehensive', action='store_true',
                       help='Run comprehensive test suite')
    parser.add_argument('--pytest', action='store_true',
                       help='Run pytest-based test suite')
    parser.add_argument('--security', action='store_true',
                       help='Run security-focused tests')
    
    # Options
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report (pytest only)')
    parser.add_argument('--markers', type=str,
                       help='Pytest markers to filter tests (e.g., "not slow")')
    parser.add_argument('--save-report', action='store_true',
                       help='Save detailed JSON report')
    parser.add_argument('--install-deps', action='store_true',
                       help='Install test dependencies before running')
    parser.add_argument('--skip-server-check', action='store_true',
                       help='Skip API server availability check')
    
    args = parser.parse_args()
    
    # If no specific test suite is selected, run all
    if not any([args.basic, args.comprehensive, args.pytest, args.security]):
        args.all = True
    
    # Create and run test runner
    runner = TestRunner(args)
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()