
class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value=value
        self.children = children
        self.props=props
        
    def to_html(self):
        raise NotImplementedError()
        
    def props_to_html(self):
        if self.props == None or self.props == {}:
            return ""
        out = ""
        for p in self.props:
            out += f" {p}=\"{self.props[p]}\""
        return out
    def rep_children(self):
        out = ""
        if(self.children == None):
            return out
        for c in self.children:
            out += str(c) + " "
        return out
    def __repr__(self):
        return f"tag: {self.tag} value: {self.value} props:{self.props_to_html()} children: [{self.rep_children()}]"
        
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)
        
    def to_html(self):
        if self.value == None:
            raise ValueError("All leaf nodes must have a value")
        if self.tag == None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)
    def to_html(self):
        if self.tag == None:
            raise ValueError("All parent nodes must have a tag")
        if self.children == None:
            raise ValueError("All parent nodes must have children")
        str = ""
        for c in self.children:
            str += (c.to_html())
        return f"<{self.tag}{self.props_to_html()}>{str}</{self.tag}>"
    def __repr__(self):
        return f"ParentNode({self.tag}, children: {self.children}, {self.props})"
