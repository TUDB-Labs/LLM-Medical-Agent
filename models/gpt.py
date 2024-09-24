from json import loads, dumps
import json
import _thread
import time
import traceback
import ipdb
from concurrent.futures import ThreadPoolExecutor

result = {}
error_count = {}
threadLock = _thread.allocate_lock()
OPENAI_API_KEY = "sk-Ei2IrBHLiFEhgFsCA4071aE63c254465A3Cf0230Cf3c8a9d"
OPENAI_BASE_URL = "https://one.aios123.com/v1/"
def _do_fun(fn, id, arg):
    global result
    try:
        ret = fn(arg)
        with threadLock:
            result[id] = ret
    except Exception:
        if id not in error_count: error_count[id] = 0
        error_count[id] += 1
        if error_count[id] > 50:
            result[id] = "ERROR"
        else:
            traceback.print_exc()
            time.sleep(0.5)
            return _do_fun(fn, id, arg)


def wait_mutil_task(fn, args: dict, mutil=20, timeout: int = 600):
    pool = ThreadPoolExecutor(mutil)
    for k, q in args.items():
        result[k] = None
        pool.submit(_do_fun, fn, k, q)
    has_pass = False
    ts = time.time()
    last_size = 0
    while not has_pass:
        has_pass = True
        ok_count = 0
        for k, v in result.copy().items():
            if v is None:
                has_pass = False
            else:
                ok_count += 1
        print(f"ok:{ok_count}/{len(args)}  {int(ok_count * 100 / len(args))}%", end="\n", flush=True)
        if time.time() - ts > timeout:
            has_pass = True
        if last_size != ok_count:
            ts = time.time()
        last_size = ok_count
        time.sleep(0.5)
    ret = result.copy()
    result.clear()
    pool.shutdown(wait=False)
    return ret


def gpt_ask_no_stream(data, question, prompt):
    message=[
                {'role': 'system',
         'content': prompt},
        {'role': 'user', 'question':question, 'content': data}
    ]
    return gpt_ask(message,stream=False)

def gpt_ask(message,stream=True,cb=None):
    import openai

    openai.api_key = OPENAI_API_KEY
    openai.base_url = OPENAI_BASE_URL 
    completion = openai.chat.completions.create(
        model="gpt-4o-mini", 
        messages=message,
        stream=stream
    )
    if stream:
        for chunk in completion:
            if chunk.choices[0].delta.content:
                cb(chunk.choices[0].delta.content)
    else:
        return completion.choices[0].message.content
def gpt_ask_json(message,stream=True,cb=None):
    import openai

    openai.api_key = OPENAI_API_KEY
    openai.base_url = OPENAI_BASE_URL 
    completion = openai.chat.completions.create(
        model="gpt-4o-mini", 
        messages=message,
        stream=stream,
        response_format={ "type": "json_object" }
    )
    if stream:
        for chunk in completion:
            if chunk.choices[0].delta.content:
                cb(chunk.choices[0].delta.content)
    else:
        return completion.choices[0].message.content
def gpt_request_from_relative_chunk_abstract(prompts, save_path):
        """"""

        def get_filter_data(prompt):
            ret= get_request_data_abstract(prompt)
            if ret=="" or "network error" in ret :
                raise Exception("error data")
            return ret
        rets = wait_mutil_task(get_filter_data, prompts, mutil=3, timeout=60) # 多线程处理 参数fn 执行的方法
        # 参数args key为任意字符串，value为传入方法的参数   参数  mutil  并发线程   参数 timeout 多久没有数据更新判定为超时,一旦超时，会立刻返回数据。
        
        with open(save_path, "w", encoding="utf8") as f:
            # value = [v for v in rets.values()][0]
            # json_value=json.loads(value)
            print(rets)
            f.write(json.dumps(rets))
        return prompts
def gpt_request_from_relative_chunk(prompts):
        """"""

        def get_filter_data(prompt):
            ret= get_request_data(prompt)
            if ret=="" or "network error" in ret :
                raise Exception("error data")
            return ret
        rets = wait_mutil_task(get_filter_data, prompts, mutil=3, timeout=60) # 多线程处理 参数fn 执行的方法
        # 参数args key为任意字符串，value为传入方法的参数   参数  mutil  并发线程   参数 timeout 多久没有数据更新判定为超时,一旦超时，会立刻返回数据。
        
        value = [v for v in rets.values()][0]
        json_value=json.loads(value)
        print(json_value)
        return json.dumps(json_value)

def gpt_request_demo(all_datas, question, prompt):
        """"""

        def get_filter_data(data):
            ret= gpt_ask_no_stream(data, question, prompt)
            
            if ret=="" or "network error" in ret or "ERROR" == ret or "ERROR " == ret  :
                raise Exception("error data")
            return ret
        # ret = get_filter_data(all_datas)
        rets = wait_mutil_task(get_filter_data, all_datas, mutil=20, timeout=60) # 多线程处理 参数fn 执行的方法
        # 参数args key为任意字符串，value为传入方法的参数   参数  mutil  并发线程   参数 timeout 多久没有数据更新判定为超时,一旦超时，会立刻返回数据。
        print(rets)
        return rets
def get_request_data(prompt):
        message=[
        {"role":"system", "content": "You are a medical literature research assistant,get information from context to answer my questions"},
        {'role': 'user', 'content': prompt }
    ]
        return gpt_ask_json(message,stream=False)

def get_request_data_icd10(prompt):
        message=[
        {"role":"system", "content": "You are a medical literature research assistant,tell me the ICD10 code of the disease"},
        {'role': 'user', 'content': prompt }
    ]
        return gpt_ask_icd10(message,stream=False)

def gpt_ask_icd10(message,stream=True,cb=None):
    import openai

    openai.api_key = OPENAI_API_KEY
    openai.base_url = OPENAI_BASE_URL
    completion = openai.chat.completions.create(
        model="gpt-4o", 
        messages=message,
        stream=stream,
        response_format={ "type": "json_object" }
    )
    if stream:
        for chunk in completion:
            if chunk.choices[0].delta.content:
                cb(chunk.choices[0].delta.content)
    else:
        return completion.choices[0].message.content

def get_request_data_abstract(prompt):
        message=[
        {"role":"system", "content": "You are a medical literature research assistant,get information from context to answer my questions"},
        {'role': 'user', 'content': prompt }
    ]
        return gpt_ask(message,stream=False)


if __name__ == "__main__":
    with open("/root/medical/midical_data/medical_paper_chunked/akkawi2009.md_doc", "r", encoding="utf8") as f:
        datas=loads(f.read())
    gpt_request_demo(datas, prompt = "Please first look for information related to the question in the document given below, and then determine whether the document is useful for you to answer the question, only answer yes or no.:")

