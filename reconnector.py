import numpy as np

# Reconnect convolution blocks inside NN:


# helper func to swap
def swap(weights, fixed, num1, num2):
    # w[:,:,fixed, num1] <=> w[:,:,fixed, num2]
    conv1vals = weights[:, :, fixed, num1]
    # print("conv1vals.shape", conv1vals.shape)
    conv2vals = weights[:, :, fixed, num2]
    # print("conv2vals.shape", conv2vals.shape)

    weights[:, :, fixed, num2] = conv1vals
    weights[:, :, fixed, num1] = conv2vals
    return weights


# reconnection of conv filters in existing net
def reconnect(net, tensor_name="128x128/Conv0_up/weight", percent_change=10, DO_ALL=True):
    weights = get_tensor(net, tensor_name)

    res = weights.shape[2]
    possible = list(range(res))
    to_select = int((res / 100.0) * percent_change)

    print("weights.shape", weights.shape, " ... selected", to_select, "from", res)

    select = np.random.choice(possible, to_select, replace=False)

    odds = []
    evens = []
    for i in range(len(select)):
        if i % 2 == 0:
            evens.append(i)
        else:
            odds.append(i)

    # print(select)
    # print(odds)
    # print(evens)

    equalizer = min(len(odds), len(evens))
    evens = evens[0:equalizer]
    odds = odds[0:equalizer]

    AS = select[odds]
    BS = select[evens]

    # print(AS)
    # print(BS)

    DO_ALL = False
    if DO_ALL:
        NUMS = list(range(res))
    else:
        how_many = int(res/4)
        NUMS = list(np.random.choice(list(range(res)), how_many))

    for first in NUMS:
        for idx in range(len(AS)):
            weights = swap(weights, first, AS[idx], BS[idx])

    set_tensor(net, tensor_name, weights)
    return net


def get_tensor_OVERRIDE(net, target_tensor):
    np_arr = net.get_var(target_tensor)
    return np_arr

original_weights_reconnect_specific = {}
def get_tensor(net, target_tensor):
    global original_weights_reconnect_specific

    """
    # first restore net
    for tensor_key in original_weights_reconnect_specific.keys():
        #print("---reloading original values for", target_tensor, "from original_weights_reconnect_specific; keys:", original_weights_reconnect_specific.keys())
        orig_val = original_weights_reconnect_specific[tensor_key]
        net.set_var(tensor_key, orig_val )
    """
    np_arr = net.get_var(target_tensor)

    if target_tensor not in original_weights_reconnect_specific:
        #print("---saving current version of ", target_tensor," into original_weights_reconnect_specific; keys:", original_weights_reconnect_specific.keys())
        # first time getting it
        original_weights_reconnect_specific[target_tensor] = np.copy( np_arr )

    """
    else:
        #print("---getting original version of the ", target_tensor)
        I_WANT_TO_RELOAD = False
        if I_WANT_TO_RELOAD:
            np_arr = np.copy( original_weights_reconnect_specific[target_tensor] )
        else:
            np_arr = original_weights_reconnect_specific[target_tensor]
    """

    return np_arr

def restore_net(net):
    for tensor_key in original_weights_reconnect_specific.keys():
        #print("---reloading original values for", target_tensor, "from original_weights_reconnect_specific; keys:", original_weights_reconnect_specific.keys())
        orig_val = original_weights_reconnect_specific[tensor_key]
        net.set_var(tensor_key, orig_val )
    return net

def set_tensor(net, target_tensor, np_arr):
    net.set_var(target_tensor, np_arr)
    return net

# editednet = reconnect(changedGs, target_tensor, percent_change)