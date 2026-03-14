import lark_oapi as lark
from lark_oapi.api.im.v1 import P2ImMessageReceiveV1

def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    print(data)

try:
    event_handler = lark.EventDispatcherHandler.builder("", "") \
        .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
        .build()
    print("Handler built successfully")
    
    # Check attributes
    print(dir(event_handler))
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
