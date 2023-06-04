# p0_backend_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**actions_actions_get**](DefaultApi.md#actions_actions_get) | **GET** /actions | Actions
[**arm_arm_get**](DefaultApi.md#arm_arm_get) | **GET** /arm | Arm
[**bounce_track_to_audio_bounce_track_to_audio_get**](DefaultApi.md#bounce_track_to_audio_bounce_track_to_audio_get) | **GET** /bounce_track_to_audio |  Bounce Track To Audio
[**check_audio_export_valid_check_audio_export_valid_get**](DefaultApi.md#check_audio_export_valid_check_audio_export_valid_get) | **GET** /check_audio_export_valid | Check Audio Export Valid
[**click_focused_track_click_focused_track_get**](DefaultApi.md#click_focused_track_click_focused_track_get) | **GET** /click_focused_track |  Click Focused Track
[**delete_saved_track_delete_saved_track_track_name_get**](DefaultApi.md#delete_saved_track_delete_saved_track_track_name_get) | **GET** /delete_saved_track/{track_name} |  Delete Saved Track
[**delete_set_set_set_id_delete**](DefaultApi.md#delete_set_set_set_id_delete) | **DELETE** /set/{set_id} | Delete Set
[**drag_matching_track_drag_matching_track_get**](DefaultApi.md#drag_matching_track_drag_matching_track_get) | **GET** /drag_matching_track |  Drag Matching Track
[**drum_rack_to_simpler_drum_rack_to_simpler_get**](DefaultApi.md#drum_rack_to_simpler_drum_rack_to_simpler_get) | **GET** /drum_rack_to_simpler | Drum Rack To Simpler
[**edit_automation_value_edit_automation_value_get**](DefaultApi.md#edit_automation_value_edit_automation_value_get) | **GET** /edit_automation_value |  Edit Automation Value
[**execute_action_actions_group_id_action_id_get**](DefaultApi.md#execute_action_actions_group_id_action_id_get) | **GET** /actions/{group_id}/{action_id} | Execute Action
[**fire_scene_to_position_fire_scene_to_position_bar_length_get**](DefaultApi.md#fire_scene_to_position_fire_scene_to_position_bar_length_get) | **GET** /fire_scene_to_position/{bar_length} | Fire Scene To Position
[**fire_scene_to_position_fire_scene_to_position_get**](DefaultApi.md#fire_scene_to_position_fire_scene_to_position_get) | **GET** /fire_scene_to_position | Fire Scene To Position
[**fire_selected_scene_fire_selected_scene_get**](DefaultApi.md#fire_selected_scene_fire_selected_scene_get) | **GET** /fire_selected_scene | Fire Selected Scene
[**get_connections_ws_connections_get**](DefaultApi.md#get_connections_ws_connections_get) | **GET** /ws/connections | Get Connections
[**go_to_group_track_go_to_group_track_get**](DefaultApi.md#go_to_group_track_go_to_group_track_get) | **GET** /go_to_group_track |  Go To Group Track
[**load_device_load_device_name_get**](DefaultApi.md#load_device_load_device_name_get) | **GET** /load_device/{name} | Load Device
[**load_drum_rack_load_drum_rack_category_subcategory_get**](DefaultApi.md#load_drum_rack_load_drum_rack_category_subcategory_get) | **GET** /load_drum_rack/{category}/{subcategory} | Load Drum Rack
[**load_matching_track_load_matching_track_get**](DefaultApi.md#load_matching_track_load_matching_track_get) | **GET** /load_matching_track | Load Matching Track
[**load_minitaur_load_minitaur_get**](DefaultApi.md#load_minitaur_load_minitaur_get) | **GET** /load_minitaur | Load Minitaur
[**load_rev2_load_rev2_get**](DefaultApi.md#load_rev2_load_rev2_get) | **GET** /load_rev2 | Load Rev2
[**open_set_set_name_open_get**](DefaultApi.md#open_set_set_name_open_get) | **GET** /set/{name}/open |  Open Set
[**play_pause_play_pause_get**](DefaultApi.md#play_pause_play_pause_get) | **GET** /play_pause | Play Pause
[**post_set_set_post**](DefaultApi.md#post_set_set_post) | **POST** /set | Post Set
[**record_unlimited_record_unlimited_get**](DefaultApi.md#record_unlimited_record_unlimited_get) | **GET** /record_unlimited | Record Unlimited
[**reload_ableton_reload_ableton_get**](DefaultApi.md#reload_ableton_reload_ableton_get) | **GET** /reload_ableton |  Reload Ableton
[**reload_script_reload_script_get**](DefaultApi.md#reload_script_reload_script_get) | **GET** /reload_script |  Reload Script
[**save_set_as_template_save_set_as_template_get**](DefaultApi.md#save_set_as_template_save_set_as_template_get) | **GET** /save_set_as_template |  Save Set As Template
[**save_track_to_sub_tracks_save_track_to_sub_tracks_get**](DefaultApi.md#save_track_to_sub_tracks_save_track_to_sub_tracks_get) | **GET** /save_track_to_sub_tracks |  Save Track To Sub Tracks
[**scroll_scene_position_fine_scroll_scene_position_fine_direction_get**](DefaultApi.md#scroll_scene_position_fine_scroll_scene_position_fine_direction_get) | **GET** /scroll_scene_position_fine/{direction} | Scroll Scene Position Fine
[**scroll_scene_position_scroll_scene_position_direction_get**](DefaultApi.md#scroll_scene_position_scroll_scene_position_direction_get) | **GET** /scroll_scene_position/{direction} | Scroll Scene Position
[**scroll_scene_tracks_scroll_scene_tracks_direction_get**](DefaultApi.md#scroll_scene_tracks_scroll_scene_tracks_direction_get) | **GET** /scroll_scene_tracks/{direction} | Scroll Scene Tracks
[**scroll_scenes_scroll_scenes_direction_get**](DefaultApi.md#scroll_scenes_scroll_scenes_direction_get) | **GET** /scroll_scenes/{direction} | Scroll Scenes
[**scroll_track_volume_scroll_track_volume_direction_get**](DefaultApi.md#scroll_track_volume_scroll_track_volume_direction_get) | **GET** /scroll_track_volume/{direction} | Scroll Track Volume
[**select_or_load_device_select_or_load_device_name_get**](DefaultApi.md#select_or_load_device_select_or_load_device_name_get) | **GET** /select_or_load_device/{name} | Select Or Load Device
[**server_state_server_state_get**](DefaultApi.md#server_state_server_state_get) | **GET** /server_state | Server State
[**show_automation_show_automation_direction_get**](DefaultApi.md#show_automation_show_automation_direction_get) | **GET** /show_automation/{direction} | Show Automation
[**show_instrument_show_instrument_get**](DefaultApi.md#show_instrument_show_instrument_get) | **GET** /show_instrument | Show Instrument
[**show_saved_tracks_show_saved_tracks_get**](DefaultApi.md#show_saved_tracks_show_saved_tracks_get) | **GET** /show_saved_tracks |  Show Saved Tracks
[**tail_logs_raw_tail_logs_raw_get**](DefaultApi.md#tail_logs_raw_tail_logs_raw_get) | **GET** /tail_logs_raw | Tail Logs Raw
[**tail_logs_tail_logs_get**](DefaultApi.md#tail_logs_tail_logs_get) | **GET** /tail_logs | Tail Logs
[**test_test_get**](DefaultApi.md#test_test_get) | **GET** /test | Test
[**toggle_clip_notes_toggle_clip_notes_get**](DefaultApi.md#toggle_clip_notes_toggle_clip_notes_get) | **GET** /toggle_clip_notes |  Toggle Clip Notes
[**toggle_reference_toggle_reference_get**](DefaultApi.md#toggle_reference_toggle_reference_get) | **GET** /toggle_reference | Toggle Reference
[**toggle_scene_loop_toggle_scene_loop_get**](DefaultApi.md#toggle_scene_loop_toggle_scene_loop_get) | **GET** /toggle_scene_loop | Toggle Scene Loop
[**update_set_set_put**](DefaultApi.md#update_set_set_put) | **PUT** /set | Update Set


# **actions_actions_get**
> list[ActionGroup] actions_actions_get()

Actions

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Actions
        api_response = api_instance.actions_actions_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->actions_actions_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[ActionGroup]**](ActionGroup.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **arm_arm_get**
> object arm_arm_get()

Arm

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Arm
        api_response = api_instance.arm_arm_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->arm_arm_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **bounce_track_to_audio_bounce_track_to_audio_get**
> object bounce_track_to_audio_bounce_track_to_audio_get()

 Bounce Track To Audio

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        #  Bounce Track To Audio
        api_response = api_instance.bounce_track_to_audio_bounce_track_to_audio_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->bounce_track_to_audio_bounce_track_to_audio_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **check_audio_export_valid_check_audio_export_valid_get**
> object check_audio_export_valid_check_audio_export_valid_get()

Check Audio Export Valid

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Check Audio Export Valid
        api_response = api_instance.check_audio_export_valid_check_audio_export_valid_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->check_audio_export_valid_check_audio_export_valid_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **click_focused_track_click_focused_track_get**
> object click_focused_track_click_focused_track_get()

 Click Focused Track

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        #  Click Focused Track
        api_response = api_instance.click_focused_track_click_focused_track_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->click_focused_track_click_focused_track_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_saved_track_delete_saved_track_track_name_get**
> object delete_saved_track_delete_saved_track_track_name_get(track_name)

 Delete Saved Track

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    track_name = 'track_name_example' # str | 

    try:
        #  Delete Saved Track
        api_response = api_instance.delete_saved_track_delete_saved_track_track_name_get(track_name)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_saved_track_delete_saved_track_track_name_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **track_name** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_set_set_set_id_delete**
> object delete_set_set_set_id_delete(set_id)

Delete Set

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    set_id = 'set_id_example' # str | 

    try:
        # Delete Set
        api_response = api_instance.delete_set_set_set_id_delete(set_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_set_set_set_id_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **set_id** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **drag_matching_track_drag_matching_track_get**
> object drag_matching_track_drag_matching_track_get()

 Drag Matching Track

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        #  Drag Matching Track
        api_response = api_instance.drag_matching_track_drag_matching_track_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->drag_matching_track_drag_matching_track_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **drum_rack_to_simpler_drum_rack_to_simpler_get**
> object drum_rack_to_simpler_drum_rack_to_simpler_get()

Drum Rack To Simpler

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Drum Rack To Simpler
        api_response = api_instance.drum_rack_to_simpler_drum_rack_to_simpler_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->drum_rack_to_simpler_drum_rack_to_simpler_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **edit_automation_value_edit_automation_value_get**
> object edit_automation_value_edit_automation_value_get()

 Edit Automation Value

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        #  Edit Automation Value
        api_response = api_instance.edit_automation_value_edit_automation_value_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->edit_automation_value_edit_automation_value_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **execute_action_actions_group_id_action_id_get**
> object execute_action_actions_group_id_action_id_get(group_id, action_id)

Execute Action

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    group_id = 56 # int | 
action_id = 56 # int | 

    try:
        # Execute Action
        api_response = api_instance.execute_action_actions_group_id_action_id_get(group_id, action_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->execute_action_actions_group_id_action_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **int**|  | 
 **action_id** | **int**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **fire_scene_to_position_fire_scene_to_position_bar_length_get**
> object fire_scene_to_position_fire_scene_to_position_bar_length_get(bar_length)

Fire Scene To Position

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    bar_length = 56 # int | 

    try:
        # Fire Scene To Position
        api_response = api_instance.fire_scene_to_position_fire_scene_to_position_bar_length_get(bar_length)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->fire_scene_to_position_fire_scene_to_position_bar_length_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bar_length** | **int**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **fire_scene_to_position_fire_scene_to_position_get**
> object fire_scene_to_position_fire_scene_to_position_get(bar_length=bar_length)

Fire Scene To Position

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    bar_length = 56 # int |  (optional)

    try:
        # Fire Scene To Position
        api_response = api_instance.fire_scene_to_position_fire_scene_to_position_get(bar_length=bar_length)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->fire_scene_to_position_fire_scene_to_position_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bar_length** | **int**|  | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **fire_selected_scene_fire_selected_scene_get**
> object fire_selected_scene_fire_selected_scene_get()

Fire Selected Scene

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Fire Selected Scene
        api_response = api_instance.fire_selected_scene_fire_selected_scene_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->fire_selected_scene_fire_selected_scene_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_connections_ws_connections_get**
> object get_connections_ws_connections_get()

Get Connections

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Get Connections
        api_response = api_instance.get_connections_ws_connections_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->get_connections_ws_connections_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **go_to_group_track_go_to_group_track_get**
> object go_to_group_track_go_to_group_track_get()

 Go To Group Track

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        #  Go To Group Track
        api_response = api_instance.go_to_group_track_go_to_group_track_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->go_to_group_track_go_to_group_track_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **load_device_load_device_name_get**
> object load_device_load_device_name_get(name)

Load Device

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    name = 'name_example' # str | 

    try:
        # Load Device
        api_response = api_instance.load_device_load_device_name_get(name)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->load_device_load_device_name_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **load_drum_rack_load_drum_rack_category_subcategory_get**
> object load_drum_rack_load_drum_rack_category_subcategory_get(category, subcategory)

Load Drum Rack

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    category = 'category_example' # str | 
subcategory = 'subcategory_example' # str | 

    try:
        # Load Drum Rack
        api_response = api_instance.load_drum_rack_load_drum_rack_category_subcategory_get(category, subcategory)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->load_drum_rack_load_drum_rack_category_subcategory_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category** | **str**|  | 
 **subcategory** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **load_matching_track_load_matching_track_get**
> object load_matching_track_load_matching_track_get()

Load Matching Track

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Load Matching Track
        api_response = api_instance.load_matching_track_load_matching_track_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->load_matching_track_load_matching_track_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **load_minitaur_load_minitaur_get**
> object load_minitaur_load_minitaur_get()

Load Minitaur

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Load Minitaur
        api_response = api_instance.load_minitaur_load_minitaur_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->load_minitaur_load_minitaur_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **load_rev2_load_rev2_get**
> object load_rev2_load_rev2_get()

Load Rev2

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Load Rev2
        api_response = api_instance.load_rev2_load_rev2_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->load_rev2_load_rev2_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **open_set_set_name_open_get**
> object open_set_set_name_open_get(name)

 Open Set

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    name = 'name_example' # str | 

    try:
        #  Open Set
        api_response = api_instance.open_set_set_name_open_get(name)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->open_set_set_name_open_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **play_pause_play_pause_get**
> object play_pause_play_pause_get()

Play Pause

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Play Pause
        api_response = api_instance.play_pause_play_pause_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->play_pause_play_pause_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_set_set_post**
> object post_set_set_post(ableton_set)

Post Set

Forwarded from midi server

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    ableton_set = p0_backend_client.AbletonSet() # AbletonSet | 

    try:
        # Post Set
        api_response = api_instance.post_set_set_post(ableton_set)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->post_set_set_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ableton_set** | [**AbletonSet**](AbletonSet.md)|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **record_unlimited_record_unlimited_get**
> object record_unlimited_record_unlimited_get()

Record Unlimited

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Record Unlimited
        api_response = api_instance.record_unlimited_record_unlimited_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->record_unlimited_record_unlimited_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reload_ableton_reload_ableton_get**
> object reload_ableton_reload_ableton_get()

 Reload Ableton

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        #  Reload Ableton
        api_response = api_instance.reload_ableton_reload_ableton_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->reload_ableton_reload_ableton_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reload_script_reload_script_get**
> object reload_script_reload_script_get()

 Reload Script

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        #  Reload Script
        api_response = api_instance.reload_script_reload_script_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->reload_script_reload_script_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_set_as_template_save_set_as_template_get**
> object save_set_as_template_save_set_as_template_get()

 Save Set As Template

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        #  Save Set As Template
        api_response = api_instance.save_set_as_template_save_set_as_template_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->save_set_as_template_save_set_as_template_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_track_to_sub_tracks_save_track_to_sub_tracks_get**
> object save_track_to_sub_tracks_save_track_to_sub_tracks_get()

 Save Track To Sub Tracks

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        #  Save Track To Sub Tracks
        api_response = api_instance.save_track_to_sub_tracks_save_track_to_sub_tracks_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->save_track_to_sub_tracks_save_track_to_sub_tracks_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scroll_scene_position_fine_scroll_scene_position_fine_direction_get**
> object scroll_scene_position_fine_scroll_scene_position_fine_direction_get(direction)

Scroll Scene Position Fine

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    direction = 'direction_example' # str | 

    try:
        # Scroll Scene Position Fine
        api_response = api_instance.scroll_scene_position_fine_scroll_scene_position_fine_direction_get(direction)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->scroll_scene_position_fine_scroll_scene_position_fine_direction_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **direction** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scroll_scene_position_scroll_scene_position_direction_get**
> object scroll_scene_position_scroll_scene_position_direction_get(direction)

Scroll Scene Position

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    direction = 'direction_example' # str | 

    try:
        # Scroll Scene Position
        api_response = api_instance.scroll_scene_position_scroll_scene_position_direction_get(direction)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->scroll_scene_position_scroll_scene_position_direction_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **direction** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scroll_scene_tracks_scroll_scene_tracks_direction_get**
> object scroll_scene_tracks_scroll_scene_tracks_direction_get(direction)

Scroll Scene Tracks

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    direction = 'direction_example' # str | 

    try:
        # Scroll Scene Tracks
        api_response = api_instance.scroll_scene_tracks_scroll_scene_tracks_direction_get(direction)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->scroll_scene_tracks_scroll_scene_tracks_direction_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **direction** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scroll_scenes_scroll_scenes_direction_get**
> object scroll_scenes_scroll_scenes_direction_get(direction)

Scroll Scenes

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    direction = 'direction_example' # str | 

    try:
        # Scroll Scenes
        api_response = api_instance.scroll_scenes_scroll_scenes_direction_get(direction)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->scroll_scenes_scroll_scenes_direction_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **direction** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **scroll_track_volume_scroll_track_volume_direction_get**
> object scroll_track_volume_scroll_track_volume_direction_get(direction)

Scroll Track Volume

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    direction = 'direction_example' # str | 

    try:
        # Scroll Track Volume
        api_response = api_instance.scroll_track_volume_scroll_track_volume_direction_get(direction)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->scroll_track_volume_scroll_track_volume_direction_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **direction** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **select_or_load_device_select_or_load_device_name_get**
> object select_or_load_device_select_or_load_device_name_get(name)

Select Or Load Device

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    name = 'name_example' # str | 

    try:
        # Select Or Load Device
        api_response = api_instance.select_or_load_device_select_or_load_device_name_get(name)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->select_or_load_device_select_or_load_device_name_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **server_state_server_state_get**
> ServerState server_state_server_state_get()

Server State

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Server State
        api_response = api_instance.server_state_server_state_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->server_state_server_state_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ServerState**](ServerState.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **show_automation_show_automation_direction_get**
> object show_automation_show_automation_direction_get(direction)

Show Automation

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    direction = 'direction_example' # str | 

    try:
        # Show Automation
        api_response = api_instance.show_automation_show_automation_direction_get(direction)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->show_automation_show_automation_direction_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **direction** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **show_instrument_show_instrument_get**
> object show_instrument_show_instrument_get()

Show Instrument

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Show Instrument
        api_response = api_instance.show_instrument_show_instrument_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->show_instrument_show_instrument_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **show_saved_tracks_show_saved_tracks_get**
> object show_saved_tracks_show_saved_tracks_get()

 Show Saved Tracks

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        #  Show Saved Tracks
        api_response = api_instance.show_saved_tracks_show_saved_tracks_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->show_saved_tracks_show_saved_tracks_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **tail_logs_raw_tail_logs_raw_get**
> object tail_logs_raw_tail_logs_raw_get()

Tail Logs Raw

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Tail Logs Raw
        api_response = api_instance.tail_logs_raw_tail_logs_raw_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->tail_logs_raw_tail_logs_raw_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **tail_logs_tail_logs_get**
> object tail_logs_tail_logs_get()

Tail Logs

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Tail Logs
        api_response = api_instance.tail_logs_tail_logs_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->tail_logs_tail_logs_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **test_test_get**
> object test_test_get()

Test

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Test
        api_response = api_instance.test_test_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->test_test_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **toggle_clip_notes_toggle_clip_notes_get**
> object toggle_clip_notes_toggle_clip_notes_get()

 Toggle Clip Notes

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        #  Toggle Clip Notes
        api_response = api_instance.toggle_clip_notes_toggle_clip_notes_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->toggle_clip_notes_toggle_clip_notes_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **toggle_reference_toggle_reference_get**
> object toggle_reference_toggle_reference_get()

Toggle Reference

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Toggle Reference
        api_response = api_instance.toggle_reference_toggle_reference_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->toggle_reference_toggle_reference_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **toggle_scene_loop_toggle_scene_loop_get**
> object toggle_scene_loop_toggle_scene_loop_get()

Toggle Scene Loop

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    
    try:
        # Toggle Scene Loop
        api_response = api_instance.toggle_scene_loop_toggle_scene_loop_get()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->toggle_scene_loop_toggle_scene_loop_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_set_set_put**
> object update_set_set_put(title, path=path)

Update Set

### Example

```python
from __future__ import print_function
import time
import p0_backend_client
from p0_backend_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = p0_backend_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with p0_backend_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = p0_backend_client.DefaultApi(api_client)
    title = 'title_example' # str | 
path = 'path_example' # str |  (optional)

    try:
        # Update Set
        api_response = api_instance.update_set_set_put(title, path=path)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->update_set_set_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **title** | **str**|  | 
 **path** | **str**|  | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

