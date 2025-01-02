from enum import Enum
from htmlnode import LeafNode, ParentNode
import re
class TextType(Enum):
    TEXT="text"
    BOLD="bold"
    ITALIC="italic"
    CODE="code"
    LINK="link"
    IMAGE="image"
block_type_paragraph = "paragraph"
block_type_heading = "heading"
block_type_code = "code"
block_type_quote = "quote"
block_type_olist = "ordered_list"
block_type_ulist = "unordered_list"
class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(node1, node2):
        return node1.text == node2.text and node1.text_type == node2.text_type and node1.url == node2.url

    def __repr__(node):
        return f"TextNode({node.text}, {node.text_type.value}, {node.url})"
def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text, None)
        case TextType.BOLD:
            return LeafNode("b", text_node.text, None)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text, None)
        case TextType.CODE:
            return LeafNode("code", text_node.text, None)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    out = []
    for node in old_nodes:
        split_nodes = node.text.split(delimiter)
        if text_type == TextType.TEXT or len(split_nodes) == 1:
            out.append(node)
        else:
            if len(split_nodes) % 2 == 0:
                raise Exception("Invalid markdown syntax: closing delimiter not found")
            for i in range(len(split_nodes)):
                if len(split_nodes[i]) != 0:
                    if i % 2 == 0:
                        out.append(TextNode(split_nodes[i], TextType.TEXT))
                    else:
                        out.append(TextNode(split_nodes[i], text_type))
    return out

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes):
    out = []
    for node in old_nodes:
        if(node.text_type == TextType.TEXT):
            val = node.text
            while len(re.findall(r'!\[([^\]]*)\]\(([^\)]*)\)', val)) > 0:
                pull = re.findall(r'!\[([^\]]*)\]\(([^\)]*)\)', val)[0]
                spl = val.split(f'![{pull[0]}]({pull[1]})', 1)
                if len(spl[0]) > 0:
                    out.append(TextNode(spl[0], TextType.TEXT))
            
                out.append(TextNode(pull[0],TextType.IMAGE,pull[1]))
                if len(spl) > 1:
                    val = spl[1]
                else:
                    val = ''
            if len(val) > 0:
                out.append(TextNode(val, TextType.TEXT))
        else:
            out.append(node)
    return out

def split_nodes_link(old_nodes):
    out = []
    for node in old_nodes:
        if(node.text_type == TextType.TEXT):
            val = node.text
            while len(re.findall(r"\[([^\]]*)\]\(([^\)]*)\)", val)) > 0:
                pull = re.findall(r'\[([^\]]*)\]\(([^\)]*)\)', val)[0]
                spl = val.split(f'[{pull[0]}]({pull[1]})', 1)
                if len(spl[0]) > 0:
                    out.append(TextNode(spl[0], TextType.TEXT))
                pull = re.findall(r"\[([^\]]*)\]\(([^\)]*)\)", val)[0]
                out.append(TextNode(pull[0],TextType.LINK,pull[1]))
                if len(spl) > 1:
                    val = spl[1]
                else:
                    val = ''
            if len(val) > 0:
                out.append(TextNode(val, TextType.TEXT))
        else:
            out.append(node)
    return out

def text_to_textnodes(text):
    node = TextNode(text, TextType.TEXT)
    nodes = [node]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    out = []
    blocks = markdown.split("\n\n")
    for b in blocks:
        stripped = b.strip(' \n')
        if len(stripped) > 0:
            out.append(stripped)
    return out

def block_to_block_type(block):
    if re.match(r"^#{1,6} ", block) != None:
        return "heading"
    if block[0:3] == "```" and block[-3:] == "```":
        return "code"
    lines = block.split("\n")
    list_type = block_list_helper(lines)
    if list_type != None:
        return list_type
    else:
        return "paragraph"

def block_list_helper(lines):
    type = ""
    count = 1
    for l in lines:
        if type == "":
            if re.match(r"^" + str(count) + r"\. ", l) != None:
                count += 1
                type = "ordered_list"
            elif re.match(r"^>", l) != None:
                type = "quote"
            elif re.match(r"^[\*\-] ", l) != None:
                type = "unordered_list"
            else:
                return None
        elif type == "ordered_list":
            if re.match(r"^" + str(count) + r"\. ", l) != None:
                count += 1
            else:
                return None
        elif type == "quote":
            if re.match(r"^>", l) == None:
                return None
        elif type == "unordered_list":
            if re.match(r"^[\*\-] ", l) == None:
                return None
    return type

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    print(block)
    print(block_type)
    if block_type == block_type_paragraph:
        return paragraph_to_html_node(block)
    if block_type == block_type_heading:
        return heading_to_html_node(block)
    if block_type == block_type_code:
        return code_to_html_node(block)
    if block_type == block_type_olist:
        return olist_to_html_node(block)
    if block_type == block_type_ulist:
        return ulist_to_html_node(block)
    if block_type == block_type_quote:
        return quote_to_html_node(block)
    raise ValueError("Invalid block type")


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block):
    
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"Invalid heading level: {level}")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("Invalid code block")
    text = block[4:-3]
    children = text_to_children(text)
    code = ParentNode("code", children)
    return ParentNode("pre", [code])


def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)


def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("Invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)
