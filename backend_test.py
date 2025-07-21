#!/usr/bin/env python3
"""
Backend API Testing for Global TV Station System
Tests all major API endpoints and functionality
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import time

# Backend URL from frontend environment
BACKEND_URL = "https://d92044bd-a4ae-4af4-874a-268cceb8552b.preview.emergentagent.com/api"

class TVStationAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        })
        
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Root Endpoint", True, f"API accessible: {data['message']}")
                    return True
                else:
                    self.log_test("Root Endpoint", False, "Missing message in response")
                    return False
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Connection error: {str(e)}")
            return False
    
    def test_init_sample_data(self):
        """Test sample data initialization"""
        try:
            response = self.session.post(f"{self.base_url}/init-data")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "initialized" in data["message"].lower():
                    self.log_test("Initialize Sample Data", True, "Sample data initialized successfully")
                    return True
                else:
                    self.log_test("Initialize Sample Data", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Initialize Sample Data", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Initialize Sample Data", False, f"Error: {str(e)}")
            return False
    
    def test_get_regions(self):
        """Test regions endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/regions")
            if response.status_code == 200:
                regions = response.json()
                if isinstance(regions, list) and len(regions) > 0:
                    # Check if we have all 6 expected regions
                    expected_regions = ["north_america", "europe", "asia", "oceania", "africa", "south_america"]
                    found_regions = [r["region"] for r in regions]
                    
                    missing_regions = set(expected_regions) - set(found_regions)
                    if not missing_regions:
                        total_channels = sum(r["channel_count"] for r in regions)
                        self.log_test("Get Regions", True, f"All 6 regions found with {total_channels} total channels", regions)
                        return True
                    else:
                        self.log_test("Get Regions", False, f"Missing regions: {missing_regions}")
                        return False
                else:
                    self.log_test("Get Regions", False, "No regions returned or invalid format")
                    return False
            else:
                self.log_test("Get Regions", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Regions", False, f"Error: {str(e)}")
            return False
    
    def test_get_channels(self):
        """Test channels endpoint without region filter"""
        try:
            response = self.session.get(f"{self.base_url}/channels")
            if response.status_code == 200:
                channels = response.json()
                if isinstance(channels, list) and len(channels) > 0:
                    # Verify channel structure
                    sample_channel = channels[0]
                    required_fields = ["id", "channel_number", "name", "region", "description", "language", "timezone"]
                    
                    missing_fields = [field for field in required_fields if field not in sample_channel]
                    if not missing_fields:
                        self.log_test("Get All Channels", True, f"Retrieved {len(channels)} channels with correct structure")
                        return True, channels
                    else:
                        self.log_test("Get All Channels", False, f"Missing fields in channel: {missing_fields}")
                        return False, None
                else:
                    self.log_test("Get All Channels", False, "No channels returned or invalid format")
                    return False, None
            else:
                self.log_test("Get All Channels", False, f"HTTP {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("Get All Channels", False, f"Error: {str(e)}")
            return False, None
    
    def test_get_channels_by_region(self):
        """Test channels endpoint with region filtering"""
        regions_to_test = ["north_america", "europe", "asia"]
        
        for region in regions_to_test:
            try:
                response = self.session.get(f"{self.base_url}/channels?region={region}")
                if response.status_code == 200:
                    channels = response.json()
                    if isinstance(channels, list):
                        # Verify all channels belong to the requested region
                        wrong_region_channels = [ch for ch in channels if ch.get("region") != region]
                        if not wrong_region_channels:
                            self.log_test(f"Get Channels - {region}", True, f"Retrieved {len(channels)} channels for {region}")
                        else:
                            self.log_test(f"Get Channels - {region}", False, f"Found {len(wrong_region_channels)} channels with wrong region")
                    else:
                        self.log_test(f"Get Channels - {region}", False, "Invalid response format")
                else:
                    self.log_test(f"Get Channels - {region}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Get Channels - {region}", False, f"Error: {str(e)}")
    
    def test_get_programs(self):
        """Test programs endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/programs")
            if response.status_code == 200:
                programs = response.json()
                if isinstance(programs, list) and len(programs) > 0:
                    # Verify program structure
                    sample_program = programs[0]
                    required_fields = ["id", "title", "description", "type", "duration_minutes"]
                    
                    missing_fields = [field for field in required_fields if field not in sample_program]
                    if not missing_fields:
                        self.log_test("Get All Programs", True, f"Retrieved {len(programs)} programs with correct structure")
                        return True, programs
                    else:
                        self.log_test("Get All Programs", False, f"Missing fields in program: {missing_fields}")
                        return False, None
                else:
                    self.log_test("Get All Programs", False, "No programs returned or invalid format")
                    return False, None
            else:
                self.log_test("Get All Programs", False, f"HTTP {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("Get All Programs", False, f"Error: {str(e)}")
            return False, None
    
    def test_get_programs_by_type(self):
        """Test programs endpoint with type filtering"""
        program_types = ["news", "sports", "movie", "series"]
        
        for prog_type in program_types:
            try:
                response = self.session.get(f"{self.base_url}/programs?type={prog_type}")
                if response.status_code == 200:
                    programs = response.json()
                    if isinstance(programs, list):
                        # Verify all programs are of the requested type
                        wrong_type_programs = [p for p in programs if p.get("type") != prog_type]
                        if not wrong_type_programs:
                            self.log_test(f"Get Programs - {prog_type}", True, f"Retrieved {len(programs)} {prog_type} programs")
                        else:
                            self.log_test(f"Get Programs - {prog_type}", False, f"Found {len(wrong_type_programs)} programs with wrong type")
                    else:
                        self.log_test(f"Get Programs - {prog_type}", False, "Invalid response format")
                else:
                    self.log_test(f"Get Programs - {prog_type}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Get Programs - {prog_type}", False, f"Error: {str(e)}")
    
    def test_live_guide(self):
        """Test live TV guide endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/live-guide")
            if response.status_code == 200:
                live_guide = response.json()
                if isinstance(live_guide, list) and len(live_guide) > 0:
                    # Verify live guide structure
                    sample_entry = live_guide[0]
                    required_fields = ["channel", "progress_percentage", "time_remaining_minutes"]
                    
                    missing_fields = [field for field in required_fields if field not in sample_entry]
                    if not missing_fields:
                        # Check if we have current programs
                        entries_with_current = [entry for entry in live_guide if entry.get("current_program")]
                        self.log_test("Live TV Guide", True, f"Retrieved live guide for {len(live_guide)} channels, {len(entries_with_current)} with current programs")
                        return True, live_guide
                    else:
                        self.log_test("Live TV Guide", False, f"Missing fields in live guide entry: {missing_fields}")
                        return False, None
                else:
                    self.log_test("Live TV Guide", False, "No live guide data returned or invalid format")
                    return False, None
            else:
                self.log_test("Live TV Guide", False, f"HTTP {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("Live TV Guide", False, f"Error: {str(e)}")
            return False, None
    
    def test_live_guide_by_region(self):
        """Test live TV guide with region filtering"""
        regions_to_test = ["north_america", "europe"]
        
        for region in regions_to_test:
            try:
                response = self.session.get(f"{self.base_url}/live-guide?region={region}")
                if response.status_code == 200:
                    live_guide = response.json()
                    if isinstance(live_guide, list):
                        # Verify all channels belong to the requested region
                        wrong_region_entries = [entry for entry in live_guide if entry.get("channel", {}).get("region") != region]
                        if not wrong_region_entries:
                            self.log_test(f"Live Guide - {region}", True, f"Retrieved live guide for {len(live_guide)} channels in {region}")
                        else:
                            self.log_test(f"Live Guide - {region}", False, f"Found {len(wrong_region_entries)} entries with wrong region")
                    else:
                        self.log_test(f"Live Guide - {region}", False, "Invalid response format")
                else:
                    self.log_test(f"Live Guide - {region}", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Live Guide - {region}", False, f"Error: {str(e)}")
    
    def test_channel_schedule(self, channels):
        """Test channel schedule endpoint"""
        if not channels or len(channels) == 0:
            self.log_test("Channel Schedule", False, "No channels available for testing")
            return
        
        # Test with first few channels
        test_channels = channels[:3]
        
        for channel in test_channels:
            channel_id = channel["id"]
            channel_name = channel["name"]
            
            try:
                # Test 24-hour schedule
                response = self.session.get(f"{self.base_url}/schedule/{channel_id}")
                if response.status_code == 200:
                    schedule = response.json()
                    if isinstance(schedule, list):
                        if len(schedule) > 0:
                            # Verify schedule structure
                            sample_entry = schedule[0]
                            required_fields = ["channel_id", "program_id", "start_time", "end_time", "program"]
                            
                            missing_fields = [field for field in required_fields if field not in sample_entry]
                            if not missing_fields:
                                self.log_test(f"Schedule - {channel_name}", True, f"Retrieved {len(schedule)} schedule entries")
                            else:
                                self.log_test(f"Schedule - {channel_name}", False, f"Missing fields: {missing_fields}")
                        else:
                            self.log_test(f"Schedule - {channel_name}", False, "No schedule entries returned")
                    else:
                        self.log_test(f"Schedule - {channel_name}", False, "Invalid response format")
                else:
                    self.log_test(f"Schedule - {channel_name}", False, f"HTTP {response.status_code}: {response.text}")
                    
                # Test 48-hour schedule
                response_48h = self.session.get(f"{self.base_url}/schedule/{channel_id}?hours=48")
                if response_48h.status_code == 200:
                    schedule_48h = response_48h.json()
                    if isinstance(schedule_48h, list) and len(schedule_48h) > len(schedule):
                        self.log_test(f"48h Schedule - {channel_name}", True, f"Retrieved {len(schedule_48h)} entries for 48 hours")
                    else:
                        self.log_test(f"48h Schedule - {channel_name}", False, "48-hour schedule not larger than 24-hour")
                else:
                    self.log_test(f"48h Schedule - {channel_name}", False, f"HTTP {response_48h.status_code}")
                    
            except Exception as e:
                self.log_test(f"Schedule - {channel_name}", False, f"Error: {str(e)}")
    
    def test_create_program(self):
        """Test creating a new program"""
        test_program = {
            "title": "Test News Program",
            "description": "A test news program for API testing",
            "type": "news",
            "duration_minutes": 30,
            "rating": "PG",
            "genre": "News"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/programs", json=test_program)
            if response.status_code == 200:
                created_program = response.json()
                if "id" in created_program and created_program["title"] == test_program["title"]:
                    self.log_test("Create Program", True, f"Successfully created program: {created_program['title']}")
                    return True
                else:
                    self.log_test("Create Program", False, "Created program missing required fields or incorrect data")
                    return False
            else:
                self.log_test("Create Program", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Program", False, f"Error: {str(e)}")
            return False
    
    def test_create_channel(self):
        """Test creating a new channel"""
        test_channel = {
            "channel_number": 999,
            "name": "Test Channel",
            "region": "north_america",
            "description": "A test channel for API testing",
            "language": "English",
            "timezone": "America/New_York"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/channels", json=test_channel)
            if response.status_code == 200:
                created_channel = response.json()
                if "id" in created_channel and created_channel["name"] == test_channel["name"]:
                    self.log_test("Create Channel", True, f"Successfully created channel: {created_channel['name']}")
                    return True
                else:
                    self.log_test("Create Channel", False, "Created channel missing required fields or incorrect data")
                    return False
            else:
                self.log_test("Create Channel", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Channel", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("=" * 80)
        print("GLOBAL TV STATION SYSTEM - BACKEND API TESTING")
        print("=" * 80)
        print(f"Testing backend at: {self.base_url}")
        print()
        
        # Test basic connectivity
        if not self.test_root_endpoint():
            print("❌ CRITICAL: Cannot connect to backend API. Stopping tests.")
            return False
        
        print()
        print("🔄 Running API Tests...")
        print("-" * 40)
        
        # Initialize sample data
        self.test_init_sample_data()
        
        # Wait a moment for data to be processed
        time.sleep(2)
        
        # Test regions
        self.test_get_regions()
        
        # Test channels
        success, channels = self.test_get_channels()
        self.test_get_channels_by_region()
        
        # Test programs
        self.test_get_programs()
        self.test_get_programs_by_type()
        
        # Test live guide
        self.test_live_guide()
        self.test_live_guide_by_region()
        
        # Test channel schedules
        if channels:
            self.test_channel_schedule(channels)
        
        # Test creation endpoints
        self.test_create_program()
        self.test_create_channel()
        
        # Summary
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"✅ PASSED: {len(passed_tests)} tests")
        print(f"❌ FAILED: {len(failed_tests)} tests")
        print(f"📊 TOTAL:  {len(self.test_results)} tests")
        
        if failed_tests:
            print()
            print("FAILED TESTS:")
            for test in failed_tests:
                print(f"  ❌ {test['test']}: {test['message']}")
        
        print()
        success_rate = (len(passed_tests) / len(self.test_results)) * 100 if self.test_results else 0
        print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = TVStationAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Backend API is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED. Check the results above.")
        sys.exit(1)