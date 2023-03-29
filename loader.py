import json

class node:
    def __init__(self, key, data, parent) -> None:
        self.mode = None         # dict, list, pure data
        self.key = key
        self.data = None
        self.parent = parent
        self.__generate__(data)

    def __generate__(self, data) -> None:
        if isinstance(data, dict):
            self.mode = "dict"
            self.data = dict()
            for k, v in data.items():
                self.data[k] = node(k, v, self)
        elif isinstance(data, list):
            self.mode = "list"
            self.data = list()
            for item in data:
                self.data.append(node(self.key, item, self))
        else:
            self.mode = "data"
            self.data = data
    
    def to_string(self, mode) -> str:
        result = ""
        if isinstance(self.data, dict):
            result += "{\"" + self.key + "\": {" if mode else "{"
            for k, v in self.data.items():
                result = result + "\"" + k + "\": " + v.to_string(False) + ", "
            result = result[0: -2] + ("}}" if mode else "}")
        elif isinstance(self.data, list):
            result += "["
            for item in self.data:
                result = result + item.to_string(False) + ", "
            result = result[0: -2] + "]"
        else:
            content = str(self.data) if (isinstance(self.data, str) == False) else ("\"" + self.data + "\"")
            result = "{\"" + self.key + "\": " + content + "}" if mode else content
        return result

if __name__ == "__main__":
    f = open("./data.txt", "r", encoding='UTF-8')
    jsonStr = f.read()
    print(jsonStr)
    rootNode = node(None, json.loads(jsonStr), None)
