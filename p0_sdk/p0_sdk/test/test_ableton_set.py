# coding: utf-8

"""
    p0_backend

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import p0_backend_client
from p0_backend_client.models.ableton_set import AbletonSet  # noqa: E501
from p0_backend_client.rest import ApiException

class TestAbletonSet(unittest.TestCase):
    """AbletonSet unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test AbletonSet
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = p0_backend_client.models.ableton_set.AbletonSet()  # noqa: E501
        if include_optional :
            return AbletonSet(
                id = '', 
                path = '', 
                title = '', 
                muted = True, 
                current_track = p0_backend_client.models.ableton_track.AbletonTrack(
                    name = '', 
                    type = '', 
                    index = 56, ), 
                selected_track = p0_backend_client.models.ableton_track.AbletonTrack(
                    name = '', 
                    type = '', 
                    index = 56, ), 
                track_count = 56, 
                drum_rack_visible = True
            )
        else :
            return AbletonSet(
                id = '',
                muted = True,
                current_track = p0_backend_client.models.ableton_track.AbletonTrack(
                    name = '', 
                    type = '', 
                    index = 56, ),
                selected_track = p0_backend_client.models.ableton_track.AbletonTrack(
                    name = '', 
                    type = '', 
                    index = 56, ),
                track_count = 56,
                drum_rack_visible = True,
        )

    def testAbletonSet(self):
        """Test AbletonSet"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
