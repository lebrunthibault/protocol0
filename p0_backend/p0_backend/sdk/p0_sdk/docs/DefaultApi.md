# p0_backend_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**activate_rev2_editor**](DefaultApi.md#activate_rev2_editor) | **GET** /activate_rev2_editor | 
[**analyze_test_audio_clip_jitter**](DefaultApi.md#analyze_test_audio_clip_jitter) | **GET** /analyze_test_audio_clip_jitter | 
[**clear_arrangement**](DefaultApi.md#clear_arrangement) | **GET** /clear_arrangement | 
[**click**](DefaultApi.md#click) | **GET** /click | 
[**click_focused_track**](DefaultApi.md#click_focused_track) | **GET** /click_focused_track | 
[**click_vertical_zone**](DefaultApi.md#click_vertical_zone) | **GET** /click_vertical_zone | 
[**close_explorer_window**](DefaultApi.md#close_explorer_window) | **GET** /close_explorer_window | 
[**close_samples_windows**](DefaultApi.md#close_samples_windows) | **GET** /close_samples_windows | 
[**close_set**](DefaultApi.md#close_set) | **GET** /close_set | 
[**crop_clip**](DefaultApi.md#crop_clip) | **GET** /crop_clip | 
[**delete_saved_track**](DefaultApi.md#delete_saved_track) | **GET** /delete_saved_track | 
[**drag_matching_track**](DefaultApi.md#drag_matching_track) | **GET** /drag_matching_track | 
[**flatten_track**](DefaultApi.md#flatten_track) | **GET** /flatten_track | 
[**hide_plugins**](DefaultApi.md#hide_plugins) | **GET** /hide_plugins | 
[**load_instrument_track**](DefaultApi.md#load_instrument_track) | **GET** /load_instrument_track | 
[**load_sample_in_simpler**](DefaultApi.md#load_sample_in_simpler) | **GET** /load_sample_in_simpler | 
[**move_to**](DefaultApi.md#move_to) | **GET** /move_to | 
[**notify_set_state**](DefaultApi.md#notify_set_state) | **GET** /notify_set_state | 
[**ping**](DefaultApi.md#ping) | **GET** /ping | 
[**post_activate_rev2_editor**](DefaultApi.md#post_activate_rev2_editor) | **GET** /post_activate_rev2_editor | 
[**reload_ableton**](DefaultApi.md#reload_ableton) | **GET** /reload_ableton | 
[**save_set**](DefaultApi.md#save_set) | **GET** /save_set | 
[**save_track_to_sub_tracks**](DefaultApi.md#save_track_to_sub_tracks) | **GET** /save_track_to_sub_tracks | 
[**search**](DefaultApi.md#search) | **GET** /search | 
[**select**](DefaultApi.md#select) | **GET** /select | 
[**select_and_copy**](DefaultApi.md#select_and_copy) | **GET** /select_and_copy | 
[**select_and_paste**](DefaultApi.md#select_and_paste) | **GET** /select_and_paste | 
[**set_clip_file_path**](DefaultApi.md#set_clip_file_path) | **GET** /set_clip_file_path | 
[**set_envelope_loop_length**](DefaultApi.md#set_envelope_loop_length) | **GET** /set_envelope_loop_length | 
[**show_error**](DefaultApi.md#show_error) | **GET** /show_error | 
[**show_hide_plugins**](DefaultApi.md#show_hide_plugins) | **GET** /show_hide_plugins | 
[**show_info**](DefaultApi.md#show_info) | **GET** /show_info | 
[**show_plugins**](DefaultApi.md#show_plugins) | **GET** /show_plugins | 
[**show_sample_category**](DefaultApi.md#show_sample_category) | **GET** /show_sample_category | 
[**show_saved_tracks**](DefaultApi.md#show_saved_tracks) | **GET** /show_saved_tracks | 
[**show_success**](DefaultApi.md#show_success) | **GET** /show_success | 
[**show_warning**](DefaultApi.md#show_warning) | **GET** /show_warning | 
[**start_profiling_single_measurement**](DefaultApi.md#start_profiling_single_measurement) | **GET** /start_profiling_single_measurement | 
[**start_set_profiling**](DefaultApi.md#start_set_profiling) | **GET** /start_set_profiling | 
[**stop_midi_server**](DefaultApi.md#stop_midi_server) | **GET** /stop_midi_server | 
[**tail_logs**](DefaultApi.md#tail_logs) | **GET** /tail_logs | 
[**toggle_ableton_button**](DefaultApi.md#toggle_ableton_button) | **GET** /toggle_ableton_button | 


# **activate_rev2_editor**
> activate_rev2_editor()



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
        api_instance.activate_rev2_editor()
    except ApiException as e:
        print("Exception when calling DefaultApi->activate_rev2_editor: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **analyze_test_audio_clip_jitter**
> analyze_test_audio_clip_jitter(clip_path)



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
    clip_path = 'clip_path_example' # str | last

    try:
        api_instance.analyze_test_audio_clip_jitter(clip_path)
    except ApiException as e:
        print("Exception when calling DefaultApi->analyze_test_audio_clip_jitter: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **clip_path** | **str**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **clear_arrangement**
> clear_arrangement()



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
        api_instance.clear_arrangement()
    except ApiException as e:
        print("Exception when calling DefaultApi->clear_arrangement: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **click**
> click(x, y)



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
    x = 56 # int | 
y = 56 # int | last

    try:
        api_instance.click(x, y)
    except ApiException as e:
        print("Exception when calling DefaultApi->click: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x** | **int**|  | 
 **y** | **int**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **click_focused_track**
> click_focused_track()



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
        api_instance.click_focused_track()
    except ApiException as e:
        print("Exception when calling DefaultApi->click_focused_track: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **click_vertical_zone**
> click_vertical_zone(x, y)



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
    x = 56 # int | 
y = 56 # int | last

    try:
        api_instance.click_vertical_zone(x, y)
    except ApiException as e:
        print("Exception when calling DefaultApi->click_vertical_zone: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x** | **int**|  | 
 **y** | **int**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **close_explorer_window**
> close_explorer_window(title)



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
    title = 'title_example' # str | last

    try:
        api_instance.close_explorer_window(title)
    except ApiException as e:
        print("Exception when calling DefaultApi->close_explorer_window: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **title** | **str**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **close_samples_windows**
> close_samples_windows()



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
        api_instance.close_samples_windows()
    except ApiException as e:
        print("Exception when calling DefaultApi->close_samples_windows: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **close_set**
> close_set(id)



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
    id = 'id_example' # str | last

    try:
        api_instance.close_set(id)
    except ApiException as e:
        print("Exception when calling DefaultApi->close_set: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **crop_clip**
> crop_clip()



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
        api_instance.crop_clip()
    except ApiException as e:
        print("Exception when calling DefaultApi->crop_clip: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_saved_track**
> delete_saved_track(track_name)



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
    track_name = 'track_name_example' # str | last

    try:
        api_instance.delete_saved_track(track_name)
    except ApiException as e:
        print("Exception when calling DefaultApi->delete_saved_track: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **track_name** | **str**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **drag_matching_track**
> drag_matching_track()



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
        api_instance.drag_matching_track()
    except ApiException as e:
        print("Exception when calling DefaultApi->drag_matching_track: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **flatten_track**
> flatten_track()



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
        api_instance.flatten_track()
    except ApiException as e:
        print("Exception when calling DefaultApi->flatten_track: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **hide_plugins**
> hide_plugins()



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
        api_instance.hide_plugins()
    except ApiException as e:
        print("Exception when calling DefaultApi->hide_plugins: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **load_instrument_track**
> load_instrument_track(instrument_name)



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
    instrument_name = 'instrument_name_example' # str | last

    try:
        api_instance.load_instrument_track(instrument_name)
    except ApiException as e:
        print("Exception when calling DefaultApi->load_instrument_track: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **instrument_name** | **str**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **load_sample_in_simpler**
> load_sample_in_simpler(sample_path)



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
    sample_path = 'sample_path_example' # str | last

    try:
        api_instance.load_sample_in_simpler(sample_path)
    except ApiException as e:
        print("Exception when calling DefaultApi->load_sample_in_simpler: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sample_path** | **str**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **move_to**
> move_to(x, y)



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
    x = 56 # int | 
y = 56 # int | last

    try:
        api_instance.move_to(x, y)
    except ApiException as e:
        print("Exception when calling DefaultApi->move_to: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x** | **int**|  | 
 **y** | **int**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **notify_set_state**
> notify_set_state(set_data)



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
    set_data = None # object | last

    try:
        api_instance.notify_set_state(set_data)
    except ApiException as e:
        print("Exception when calling DefaultApi->notify_set_state: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **set_data** | [**object**](.md)| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **ping**
> ping()



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
        api_instance.ping()
    except ApiException as e:
        print("Exception when calling DefaultApi->ping: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_activate_rev2_editor**
> post_activate_rev2_editor()



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
        api_instance.post_activate_rev2_editor()
    except ApiException as e:
        print("Exception when calling DefaultApi->post_activate_rev2_editor: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reload_ableton**
> reload_ableton()



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
        api_instance.reload_ableton()
    except ApiException as e:
        print("Exception when calling DefaultApi->reload_ableton: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_set**
> save_set()



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
        api_instance.save_set()
    except ApiException as e:
        print("Exception when calling DefaultApi->save_set: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_track_to_sub_tracks**
> save_track_to_sub_tracks()



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
        api_instance.save_track_to_sub_tracks()
    except ApiException as e:
        print("Exception when calling DefaultApi->save_track_to_sub_tracks: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search**
> search(search)



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
    search = 'search_example' # str | last

    try:
        api_instance.search(search)
    except ApiException as e:
        print("Exception when calling DefaultApi->search: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search** | **str**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **select**
> select(question, options, vertical=vertical, color=color)



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
    question = 'question_example' # str | 
options = None # object | 
vertical = True # bool |  (optional) (default to True)
color = 'INFO' # str | last (optional) (default to 'INFO')

    try:
        api_instance.select(question, options, vertical=vertical, color=color)
    except ApiException as e:
        print("Exception when calling DefaultApi->select: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **question** | **str**|  | 
 **options** | [**object**](.md)|  | 
 **vertical** | **bool**|  | [optional] [default to True]
 **color** | **str**| last | [optional] [default to &#39;INFO&#39;]

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **select_and_copy**
> select_and_copy()



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
        api_instance.select_and_copy()
    except ApiException as e:
        print("Exception when calling DefaultApi->select_and_copy: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **select_and_paste**
> select_and_paste()



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
        api_instance.select_and_paste()
    except ApiException as e:
        print("Exception when calling DefaultApi->select_and_paste: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_clip_file_path**
> set_clip_file_path(file_path)



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
    file_path = 'file_path_example' # str | last

    try:
        api_instance.set_clip_file_path(file_path)
    except ApiException as e:
        print("Exception when calling DefaultApi->set_clip_file_path: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_path** | **str**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_envelope_loop_length**
> set_envelope_loop_length(length)



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
    length = 56 # int | last

    try:
        api_instance.set_envelope_loop_length(length)
    except ApiException as e:
        print("Exception when calling DefaultApi->set_envelope_loop_length: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **length** | **int**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **show_error**
> show_error(message)



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
    message = 'message_example' # str | last

    try:
        api_instance.show_error(message)
    except ApiException as e:
        print("Exception when calling DefaultApi->show_error: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **message** | **str**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **show_hide_plugins**
> show_hide_plugins()



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
        api_instance.show_hide_plugins()
    except ApiException as e:
        print("Exception when calling DefaultApi->show_hide_plugins: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **show_info**
> show_info(message, centered=centered)



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
    message = 'message_example' # str | 
centered = False # bool | last (optional) (default to False)

    try:
        api_instance.show_info(message, centered=centered)
    except ApiException as e:
        print("Exception when calling DefaultApi->show_info: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **message** | **str**|  | 
 **centered** | **bool**| last | [optional] [default to False]

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **show_plugins**
> show_plugins()



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
        api_instance.show_plugins()
    except ApiException as e:
        print("Exception when calling DefaultApi->show_plugins: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **show_sample_category**
> show_sample_category(category)



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
    category = 'category_example' # str | last

    try:
        api_instance.show_sample_category(category)
    except ApiException as e:
        print("Exception when calling DefaultApi->show_sample_category: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category** | **str**| last | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **show_saved_tracks**
> show_saved_tracks()



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
        api_instance.show_saved_tracks()
    except ApiException as e:
        print("Exception when calling DefaultApi->show_saved_tracks: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **show_success**
> show_success(message, centered=centered)



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
    message = 'message_example' # str | 
centered = False # bool | last (optional) (default to False)

    try:
        api_instance.show_success(message, centered=centered)
    except ApiException as e:
        print("Exception when calling DefaultApi->show_success: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **message** | **str**|  | 
 **centered** | **bool**| last | [optional] [default to False]

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **show_warning**
> show_warning(message, centered=centered)



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
    message = 'message_example' # str | 
centered = False # bool | last (optional) (default to False)

    try:
        api_instance.show_warning(message, centered=centered)
    except ApiException as e:
        print("Exception when calling DefaultApi->show_warning: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **message** | **str**|  | 
 **centered** | **bool**| last | [optional] [default to False]

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_profiling_single_measurement**
> start_profiling_single_measurement()



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
        api_instance.start_profiling_single_measurement()
    except ApiException as e:
        print("Exception when calling DefaultApi->start_profiling_single_measurement: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_set_profiling**
> start_set_profiling()



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
        api_instance.start_set_profiling()
    except ApiException as e:
        print("Exception when calling DefaultApi->start_set_profiling: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stop_midi_server**
> stop_midi_server()



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
        api_instance.stop_midi_server()
    except ApiException as e:
        print("Exception when calling DefaultApi->stop_midi_server: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **tail_logs**
> tail_logs()



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
        api_instance.tail_logs()
    except ApiException as e:
        print("Exception when calling DefaultApi->tail_logs: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **toggle_ableton_button**
> toggle_ableton_button(x, y, activate=activate)



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
    x = 56 # int | 
y = 56 # int | 
activate = False # bool | last (optional) (default to False)

    try:
        api_instance.toggle_ableton_button(x, y, activate=activate)
    except ApiException as e:
        print("Exception when calling DefaultApi->toggle_ableton_button: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x** | **int**|  | 
 **y** | **int**|  | 
 **activate** | **bool**| last | [optional] [default to False]

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

