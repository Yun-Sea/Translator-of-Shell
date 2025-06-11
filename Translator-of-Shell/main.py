import requests
import bs4
import argparse


def transition(input_str: str) -> bs4.BeautifulSoup | None:
    """
    翻译传入的词语，转换为 bs4.element.Tag 对象，检查并返回
    :param input_str:str
    :return content:bs4.element.Tag
    """
    print("正在尝试连接翻译网站...")
    url = f"https://dict.youdao.com/result?word={input_str}&lang=en"
    try:
        r = requests.get(url)
        print(f"状态码:{r.status_code}")
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        return soup.find('section', class_='modules')
    except requests.RequestException as e:
        print(f"网络请求失败: {e}")
        return None


def is_valid_content(input_str, check_content) -> bs4.element.Tag | None:
    """
    判断翻译状态，并返回内容
    :param input_str:
    :param check_content:
    :return:
    """
    content = check_content.text
    if content == "":
        print(f"抱歉，没有找到「{input_str}」相关的词")
        return None
    elif check_content.find('div', class_='maybe'):
        maybe_div = check_content.find('div', class_='maybe')
        for word_div in maybe_div.find_all('div', class_='maybe_word'):
            word = word_div.find('a', class_='point').get_text(strip=True)
            trans = word_div.find('p', class_='maybe_trans').get_text(strip=True)
            print(f"  {word}: {trans}")
        return None
    else:
        return check_content


def content_parse(content: bs4.element.Tag):
    # 解析查询的内容标题
    title = content.find('div', class_='word-head').find_all('div')[0].contents[0]
    print("标题", title)

    try:
        # 英文翻译中文

        # 发音(如果有)
        pronounce = content.find('div', class_='phone_con')
        if pronounce:
            print("发音：", pronounce.text)

        # 基本释义
        basics = content.find('ul', class_='basic').find_all('li')
        print("基本释义：")
        for basic in basics:
            print(basic.text)

    except Exception as e:
        # 中文翻译英文
        f = content.find_all('div', class_='trans-container')[1].contents[0]
        print(f.text)


def content_parse_more(content: bs4.element.Tag):
    """
    -a 参数，解析更多内容
    :param content:
    :return:
    """

    webPhrases = content.find('div', class_='webPhrase').find_all('li')
    for webPhrase in webPhrases:
        print(webPhrase.text)

    blng = content.find('div', class_='blng_sents_part').find_all('li')
    for bln in blng:
        print(bln.text)


def main():
    parser = argparse.ArgumentParser(
        description="Xpf 开发的命令行翻译工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
    python translator.py hello       # 翻译单词hello
    python translator.py 你好 -a     # 翻译"你好"并显示详细信息"""
    )

    # 添加参数
    parser.add_argument(
        'query',
        help='要翻译的内容(英文或中文)'
    )
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='显示详细翻译信息(包括网络短语和双语例句)'
    )

    args = parser.parse_args()

    # 根据参数执行操作
    word = args.query
    t_str = transition(word)
    if t_str is None:
        print("转换失败！")
        return
    if is_valid_content(word, t_str) is None:
        return
    content_parse(t_str)
    if args.all:
        content_parse_more(t_str)


if __name__ == '__main__':
    # url = 'https://dict.youdao.com/'
    main()
