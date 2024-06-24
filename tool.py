import cv2
import datetime
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis, MultiModalConversation
import os

os.environ['OPENCV_VIDEOIO_PLUGIN_LIST'] = 'v4l2,camera'
# import OPi.GPIO as GPIO

# 定义工具列表，模型在选择使用哪个工具时会参考工具的name和description
tools = [
    # 工具1 拍摄一张图片来识别
    {
        "type": "function",
        "function": {
            "name": "identify_images",
            "description": "当问你看到了什么时，你可以使用这个工具",
            "parameters": {}  # 因为无需输入参数，因此parameters为空字典
        }
    },
    # 工具2 拍摄当前的图片保存下来
    {
        "type": "function",
        "function": {
            "name": "take_photo",
            "description": "当让你记下现在看到的东西或者拍摄当前的场景或者拍一张照片时，你可以使用这个工具",
            "parameters": {}  # 因为无需输入参数，因此parameters为空字典
        }
    },
    # 工具3 绘制图片
    {
        "type": "function",
        "function": {
            "name": "draw_picture",
            "description": "当你想根据用户描述绘制图片时，你可以使用这个工具。",
            "parameters": {  # 用户描述想要绘制的图片，因此参数设置为description
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "des": "转换成英文的用户对绘制图片的描述。"
                    }
                }
            },
            "required": [
                "des"
            ]
        }
    },
    # 工具4 获取当前时间
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "当用户想要获取当前时间，或者用户问你现在几点了时，你可以使用这个工具。",
            "parameters": {}  # 因为无需输入参数，因此parameters为空字典
        }
    },
    # # 工具5 开启风扇
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "turn_on_fan",
    #         "description": "当你想开启风扇时，或者我说开启风扇时，你可以使用这个工具。",
    #         "parameters": {}
    #     }
    # },
    # # 工具6 关闭风扇
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "turn_off_fan",
    #         "description": "当你想要关闭风扇时，或者我说关闭风扇时，你可以使用这个工具。",
    #         "parameters": {}
    #     }
    # },
    {
        "type": "function",
        "function": {
            "name": "miaomiao",
            "description": "当用户想要你喵喵叫时，你可以使用这个工具。",
            "parameters": {}  # 因为无需输入参数，因此parameters为空字典
        }
    },

]


def identify_images():
    local_file_path = 'file://data/image.jpg'
    # 打开默认的摄像头
    camera = cv2.VideoCapture(0)

    # 捕获一帧图像
    ret, frame = camera.read()
    if not ret:
        print("无法捕获图像")
        return

    # 保存图像到当前工作目录
    image_path = "image.jpg"
    cv2.imwrite('data/image.jpg', frame)

    # 释放摄像头资源
    camera.release()

    print(f"图像已保存至: {image_path}")
    messages = [{
        'role': 'system',
        'content': [{
            'text': 'You are a helpful assistant.'
        }]
    }, {
        'role':
            'user',
        'content': [
            {
                'image': local_file_path
            },
            {
                'text': '你看到了什么?'
            },
        ]
    }]
    response = MultiModalConversation.call(model='qwen-vl-max', messages=messages)
    print(response.output.choices[0].message.content[0]['text'])
    return response.output.choices[0].message.content[0]['text']


def take_photo():
    # 获取当前时间并格式化为字符串
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    local_file_path = f"data/image_{current_time}.jpg"

    # 打开默认的摄像头
    camera = cv2.VideoCapture(0)

    # 捕获一帧图像
    ret, frame = camera.read()
    if not ret:
        print("无法捕获图像")
        return

    # 保存图像到当前工作目录，文件名为当前时间
    image_path = local_file_path
    cv2.imwrite(image_path, frame)

    # 释放摄像头资源
    camera.release()

    print(f"图像已保存至: {image_path}")
    return f'图片已记录下来了喵！'


def draw_picture(description):
    rsp = ImageSynthesis.call(model='stable-diffusion-xl',
                              prompt=description,
                              negative_prompt="garfield",
                              n=1,
                              size='1024*1024')
    if rsp.status_code == HTTPStatus.OK:
        print(rsp.output)
        print(rsp.usage)
        # save file to current directory
        for result in rsp.output.results:
            file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
            with open('./data/%s' % file_name, 'wb+') as f:
                f.write(requests.get(result.url).content)
                return f'图片已保存下来了喵！'
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))


def get_current_time():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"当前时间是: {current_time}喵！")
    return current_time


# def turn_on_fan():
#     # 初始化GPIO
#     GPIO.setmode(GPIO.BOARD)
#
#     # 选择一个有效的GPIO引脚，例如GPIO75
#     led_pin = 8
#
#     # 设置GPIO引脚为输出模式
#     GPIO.setup(led_pin, GPIO.OUT)
#
#     GPIO.output(led_pin, GPIO.HIGH)
#     GPIO.cleanup()
#     print("开启风扇喵！")
#     return "开启风扇喵！"
#
# def turn_off_fan():
#     GPIO.setmode(GPIO.BOARD)
#     led_pin = 8
#     GPIO.setup(led_pin, GPIO.OUT)
#     GPIO.output(led_pin, GPIO.LOW)
#     GPIO.cleanup()
#     print("关闭风扇喵！")
#     return "关闭风扇喵！"

def miaomiao():
    print("喵喵喵工具调用成功")
    return '喵喵喵'

TOOL_MAP = {
    'identify_images': identify_images,  # 识别图像
    'take_photo': take_photo,  # 拍照
    'get_current_time': get_current_time,  # 获取当前时间
    # 'turn_on_fan': turn_on_fan,  # 开启风扇
    # 'turn_off_fan': turn_off_fan  # 关闭风扇
    'miaomiao': miaomiao,
}

TOOL_MAP_1 = {
    'draw_picture': draw_picture,  # 画图'
}
