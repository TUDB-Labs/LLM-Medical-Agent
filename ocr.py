import concurrent
from concurrent.futures.thread import ThreadPoolExecutor

import numpy as np
import requests
import pickle
import base64
import cv2


def decode_data(data):
    return pickle.loads(base64.decodebytes(bytes(data, "utf-8")))


def encode_data(data):
    return base64.b64encode(pickle.dumps(data)).decode("utf-8")


def ocr(img):
    ret = requests.post("https://ocr.k3s.tudb.work/ocr",
                        json={"img": encode_data(img)}).text
    ret = decode_data(ret)
    return ret


def download_file(url):
    return url,requests.get(url).content
def ocr_urls(urls):
    # 下载文件并进行ocr
    #并发下载
    executor = ThreadPoolExecutor(max_workers=10)
    futures = [executor.submit(download_file, url) for url in urls]
    img_datas = dict([future.result() for future in concurrent.futures.as_completed(futures)])
    img_num_list=[]
    img_url_list=[]
    for url,img in img_datas.items():
        if img:
            img_buffer_numpy = np.frombuffer(img, dtype=np.uint8)  # 将 图片字节码bytes  转换成一维的numpy数组 到缓存中
            img_numpy = cv2.imdecode(img_buffer_numpy, 1)  # 从指定的内存缓存中读取一维numpy数据，并把数据转换(解码)成图像矩阵格式
            img_num_list.append(img_numpy)
            img_url_list.append(url)
    rets=ocrs(img_num_list)
    return_list=[]
    for u in urls:
        if u in img_url_list:
            idx=img_url_list.index(u)
            return_list.append(rets[idx])
        else:
            return_list.append(None)
    return return_list




def ocrs(imgs: list):
    ret = requests.post("https://ocr.k3s.tudb.work/ocrs",
                        json={"imgs": encode_data(imgs)}).text
    import ipdb
    ipdb.set_trace()
    ret = decode_data(ret)
    return ret


def recognize(img, box):
    ret = requests.post("https://ocr.k3s.tudb.work/recognize",
                        json={"img": encode_data(img), "box": encode_data(box)}).text
    ret = decode_data(ret)
    return ret


def ocr_img(img):
    nd = np.array(img)
    ret = requests.post("https://ocr.k3s.tudb.work/detect", json={"img": encode_data(nd)}).text
    ret = decode_data(ret)
    # print(ret)

    bxs = ret
    if not bxs:
        return None

    bxs = [(line[0], line[1][0]) for line in bxs]

    def deal_b(b):
        if b[0][0] <= b[1][0] and b[0][1] <= b[-1][1]:
            left, right, top, bott = b[0][0], b[1][0], b[0][1], b[-1][1]
            text = recognize(nd,
                             np.array([[left, top], [right, top], [right, bott], [left, bott]],
                                      dtype=np.float32))
            return {"box": {"left": left, "top": top, "right": right, "bottom": bott}, "text": text}
        else:
            return None

    results = []
    # for b,t in bxs:
    #     results.append(deal_b(b))
    with ThreadPoolExecutor(6) as executor:
        # 提交任务给线程池
        futures = [executor.submit(deal_b, b) for b, t in bxs]
        # 获取结果
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    return results


def format_result(data):
    formatted_output = []
    for box, (text, _) in data:
        y = box[0][1]
        formatted_output.append((y, text))

    # Sort by y coordinate to maintain order of appearance
    formatted_output.sort(key=lambda x: x[0])
    out_text = ""
    # Print the formatted text with appropriate spacing
    previous_y = 0
    for y, text in formatted_output:
        # Calculate spacing based on position
        if previous_y == 0:
            # First entry, print normally
            out_text += text
        else:
            # Print with line breaks if there is a significant gap
            if (y - previous_y) > 20:  # Adjust the threshold as needed
                out_text += "\n" + text
            else:
                out_text += " " + text
        previous_y = y
    return out_text


if __name__ == "__main__":
    import cv2
    from ocr import ocr_img, ocr
    from pdf2image import convert_from_path

    # 将 PDF 转换为图像列表，每个图像对应一页


    # 设置 PDF 文件路径
    # pdf_path = '/root/LLM-Medical-Agent/341337.pdf'

    # 将 PDF 文件转换为图片
    # images = convert_from_path(pdf_path)

    # # 保存转换后的图片
    # for i, image in enumerate(images):
    #     image.save(f'/root/LLM-Medical-Agent/pngs/page_{i+1}.png', 'PNG')

    # print("PDF 文件已成功转换为图片")
    # print(type(images))
    img = cv2.imread("/root/LLM-Medical-Agent/pngs/page_1.png")
    data = ocr(img)
    print(data)
    ret = format_result(data)
    print(ret)
