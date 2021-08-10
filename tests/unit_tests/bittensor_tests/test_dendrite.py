

from bittensor._endpoint import endpoint
import torch
import pytest
import time
import bittensor

wallet =  bittensor.wallet(
    path = '/tmp/pytest',
    name = 'pytest',
    hotkey = 'pytest',
) 
wallet.create_new_coldkey(use_password=False, overwrite = True)
wallet.create_new_hotkey(use_password=False, overwrite = True)

dendrite = bittensor.dendrite( wallet = wallet )
neuron_obj = bittensor.endpoint(
    uid = 0,
    ip = '0.0.0.0',
    ip_type = 4,
    port = 12345,
    hotkey = dendrite.wallet.hotkey.public_key,
    coldkey = dendrite.wallet.coldkey.public_key,
    modality = 0
)

def test_dendrite_forward_text_endpoints_tensor():
    endpoints = neuron_obj.to_tensor()
    x = torch.tensor( [[ 1,2,3 ], [ 1,2,3 ]] )
    resp1, _ = dendrite.forward_text( endpoints, x )
    assert list(resp1.shape) == [1, 2, 3, bittensor.__network_dim__]

def test_dendrite_forward_text_multiple_endpoints_tensor():
    endpoints_1 = neuron_obj.to_tensor()
    endpoints_2 = neuron_obj.to_tensor()
    endpoints = torch.stack( [endpoints_1, endpoints_2], dim=0)
    x = torch.tensor( [[ 1,2,3 ], [ 1,2,3 ]] )
    resp1, _ = dendrite.forward_text( endpoints, x )
    assert list(resp1.shape) == [2, 2, 3, bittensor.__network_dim__]

def test_dendrite_forward_text_multiple_endpoints_tensor_list():
    endpoints_1 = neuron_obj.to_tensor()
    endpoints_2 = neuron_obj.to_tensor()
    endpoints_3 = neuron_obj.to_tensor()
    endpoints = [torch.stack( [endpoints_1, endpoints_2], dim=0), endpoints_3]
    x = torch.tensor( [[ 1,2,3 ], [ 1,2,3 ]] )
    resp1, _ = dendrite.forward_text( endpoints, x )
    assert list(resp1.shape) == [3, 2, 3, bittensor.__network_dim__]

def test_dendrite_forward_text_singular():
    x = torch.tensor( [[ 1,2,3 ], [ 1,2,3 ]] )
    resp1, _ = dendrite.forward_text( [neuron_obj], x )
    assert list(resp1.shape) == [1, 2, 3, bittensor.__network_dim__]
    resp2, _ = dendrite.forward_text( [neuron_obj], [x] )
    assert list(resp2.shape) == [1, 2, 3, bittensor.__network_dim__]
    resp3, _ = dendrite.forward_text( [neuron_obj, neuron_obj], x )
    assert list(resp3.shape) == [2, 2, 3, bittensor.__network_dim__]
    with pytest.raises(ValueError):
        dendrite.forward_text( [neuron_obj, neuron_obj], [x] )

def test_dendrite_forward_text_singular_no_batch_size():
    x = torch.tensor( [ 1,2,3 ] )
    resp1, _ = dendrite.forward_text( [neuron_obj], x )
    assert list(resp1.shape) == [1, 1, 3, bittensor.__network_dim__]
    resp2, _ = dendrite.forward_text( [neuron_obj], [x] )
    assert list(resp2.shape) == [1, 1, 3, bittensor.__network_dim__]
    resp3, _ = dendrite.forward_text( [neuron_obj, neuron_obj], x )
    assert list(resp3.shape) == [2, 1, 3, bittensor.__network_dim__]
    with pytest.raises(ValueError):
        dendrite.forward_text( [neuron_obj, neuron_obj], [x] )

def test_dendrite_forward_text_tensor_list_singular():
    x = [ torch.tensor( [ 1,2,3 ] ) for _ in range(2) ]
    with pytest.raises(ValueError):
        resp1, _ = dendrite.forward_text( [neuron_obj], x )
    resp1, _ = dendrite.forward_text( [neuron_obj, neuron_obj], x )
    assert list(resp1.shape) == [2, 1, 3, bittensor.__network_dim__]

def test_dendrite_forward_text_tensor_list():
    x = [ torch.tensor( [[ 1,2,3 ], [ 1,2,3 ]] ) for _ in range(2) ]
    with pytest.raises(ValueError):
        resp1, _ = dendrite.forward_text( [neuron_obj], x )
    resp1, _ = dendrite.forward_text( [neuron_obj, neuron_obj], x )
    assert list(resp1.shape) == [2, 2, 3, bittensor.__network_dim__]

def test_dendrite_forward_text_singular_string():
    x = "the cat"
    resp1, _ = dendrite.forward_text( [neuron_obj], x )
    assert list(resp1.shape) == [1, 1, 2, bittensor.__network_dim__]
    resp2, _ = dendrite.forward_text( [neuron_obj], [x] )
    assert list(resp2.shape) == [1, 1, 2, bittensor.__network_dim__]
    resp3, _ = dendrite.forward_text( [neuron_obj, neuron_obj], x )
    assert list(resp3.shape) == [2, 1, 2, bittensor.__network_dim__]
    resp4, _ = dendrite.forward_text( [neuron_obj, neuron_obj], [x] )
    assert list(resp4.shape) == [2, 1, 2, bittensor.__network_dim__]

def test_dendrite_forward_text_list_string():
    x = ["the cat", 'the dog', 'the very long sentence that needs to be padded']
    resp1, _ = dendrite.forward_text( [neuron_obj], x )
    assert list(resp1.shape) == [1, 3, 9, bittensor.__network_dim__]
    resp2, _ = dendrite.forward_text( [neuron_obj, neuron_obj], x )
    assert list(resp2.shape) == [2, 3, 9, bittensor.__network_dim__]

def test_dendrite_forward_tensor_shape_error():
    x = torch.rand(3, 3, 3, dtype=torch.float32)
    with pytest.raises(ValueError):
        dendrite.forward_tensor( [neuron_obj], [x])

def test_dendrite_forward_image_shape_error():
    x = torch.rand(3, 3, 3, dtype=torch.float32)
    with pytest.raises(ValueError):
        dendrite.forward_image( [neuron_obj], [x])

def test_dendrite_forward_text_shape_error():
    x = torch.zeros((3, 3, 3), dtype=torch.int64)
    with pytest.raises(ValueError):
        dendrite.forward_image( [neuron_obj], [x])

def test_dendrite_forward_text():
    x = torch.tensor([[1,2,3,4],[5,6,7,8]], dtype=torch.long)
    out, ops = dendrite.forward_text( [neuron_obj], [x])
    assert ops[0].item() == bittensor.proto.ReturnCode.Unavailable
    assert list(out[0].shape) == [2, 4, bittensor.__network_dim__]

def test_dendrite_forward_image():
    x = torch.tensor([ [ [ [ [ 1 ] ] ] ] ], dtype=torch.float32)
    out, ops = dendrite.forward_image( [neuron_obj], [x])
    assert ops[0].item() == bittensor.proto.ReturnCode.Unavailable
    assert list(out[0].shape) == [1, 1, bittensor.__network_dim__]

def test_dendrite_forward_tensor():
    x = torch.rand(3, 3, bittensor.__network_dim__, dtype=torch.float32)
    out, ops = dendrite.forward_tensor( [neuron_obj], [x])
    assert ops[0].item() == bittensor.proto.ReturnCode.Unavailable
    assert list(out[0].shape) == [3, 3, bittensor.__network_dim__]

def test_dendrite_backoff():
    _dendrite = bittensor.dendrite( wallet = wallet )
    _endpoint_obj = bittensor.endpoint(
        uid = 0,
        ip = '0.0.0.0',
        ip_type = 4,
        port = 12345,
        hotkey = _dendrite.wallet.hotkey.public_key,
        coldkey = _dendrite.wallet.coldkey.public_key,
        modality = 0
    )
    print (_endpoint_obj)
    
    # Normal call.
    x = torch.rand(3, 3, bittensor.__network_dim__, dtype=torch.float32)
    out, ops = _dendrite.forward_tensor( [_endpoint_obj], [x])
    assert ops[0].item() == bittensor.proto.ReturnCode.Unavailable
    assert list(out[0].shape) == [3, 3, bittensor.__network_dim__]


if __name__ == "__main__":
    # test_dendrite_forward_tensor_shape_error ()
    # test_dendrite_forward_image_shape_error ()
    # test_dendrite_forward_text_shape_error ()
    # test_dendrite_forward_text ()
    # test_dendrite_forward_image ()
    # test_dendrite_forward_tensor ()
    # test_dendrite_backoff ()
    # test_dendrite_forward_text_singular_no_batch_size()
    # test_dendrite_forward_text_singular()
    # test_dendrite_forward_text_singular_string()
    # test_dendrite_forward_text_list_string()
    # test_dendrite_forward_text_tensor_list_singular()
    # test_dendrite_forward_text_tensor_list()
    # test_dendrite_forward_text_endpoints_tensor()
    test_dendrite_forward_text_multiple_endpoints_tensor()
    test_dendrite_forward_text_multiple_endpoints_tensor_list()