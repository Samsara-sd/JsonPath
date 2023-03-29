from loader import node
import jsonpathParser, json, sys
from jsonpathParser import operation

def getDescendant(jnode: node, attr: str, resultSet: set[node]):
    if jnode.mode == "data":
        return
    elif jnode.mode == "dict":
        if attr in jnode.data:
            if isinstance(jnode.data[attr].data, list):
                for sonjn in jnode.data[attr].data:
                    resultSet.add(sonjn)
            else:
                resultSet.add(jnode.data[attr])
        elif attr == "node()" or attr == "text()":
            for k, v in jnode.data.items():
                if isinstance(v, list):
                    for item in v:
                        resultSet.add(item)
                else:
                    resultSet.add(v) 
        for k, v in jnode.data.items():
            getDescendant(v, attr, resultSet)
    elif jnode.mode == "list":
        for item in jnode.data:
            getDescendant(item, attr, resultSet)


def execute(jnode: node, operationList: list[operation]):
    try:
        nodeList = [jnode] if isinstance(jnode.data, list) == False else [d for d in jnode.data]
        for operation in operationList:
            nextSet = set()
            if operation.aggr is not None:  # 聚合操作
                dataList = nodeList.copy()
                if len(dataList) != 0 and isinstance(dataList[0], node): 
                    dataList = [jn.data for jn in dataList]
                if operation.aggr == "count":
                    nextSet.add(len(dataList))
                elif operation.aggr == "sum":
                    nextSet.add(sum(dataList))
                elif operation.aggr == "avg":
                    nextSet.add(sum(dataList) / len(dataList))
                elif operation.aggr == "max":
                    nextSet.add(max(dataList))
                elif operation.aggr == "min":
                    nextSet.add(min(dataList))
            else: # 寻路操作
                # 1. 根据轴类型和属性名，选定这一步要处理的节点范围。
                # 这里的处理结果只能有两种情况：dict对象或者pure data。对于list，提取所有的子元素，不能把list下传。
                attr = operation.attr
                for jn in nodeList:
                    if operation.axis == "child":
                        if attr in jn.data:
                            if isinstance(jn.data[attr].data, list):
                                for sonjn in jn.data[attr].data:
                                    nextSet.add(sonjn)
                            else:
                                nextSet.add(jn.data[attr])
                        elif attr == "node()" or attr == "text()":
                            for k, v in jn.data.items():
                                if isinstance(v, list):
                                    for item in v:
                                        nextSet.add(item)
                                else:
                                   nextSet.add(v) 
                    elif operation.axis == "descendant":
                        getDescendant(jn, attr, nextSet)
                    elif operation.axis == "descendant-or-self":
                        if jn.key == attr:
                            nextSet.add(jn)
                        getDescendant(jn, attr, nextSet)
                    elif operation.axis == "parent":
                        jnp = jn.parent
                        if attr == "node()" or attr == "text()" or jnp.key == attr:
                            nextSet.add(jnp)
                    elif operation.axis == "ancestor":
                        jnp = jn.parent
                        while jnp is not None:
                            if attr == "node()" or attr == "text()" or jnp.key == attr:
                                nextSet.add(jnp)
                            jnp = jnp.parent
                    elif operation.axis == "ancestor-or-self":
                        if attr == "node()" or attr == "text()" or jn.key == attr:
                            nextSet.add(jn)
                        jnp = jn.parent
                        while jnp is not None:
                            if attr == "node()" or attr == "text()" or jnp.key == attr:
                                nextSet.add(jnp)
                            jnp = jnp.parent
                    elif operation.axis == "self":
                        if attr == "node()" or attr == "text()" or jn.key == attr:
                            nextSet.add(jn)

            nextList = list(nextSet) # 去重
            nextList = [item.data for item in nextList] if len(nextList) > 0 and isinstance(nextList[0], node) and attr == "text()" else nextList
            # 2. 如果有谓词条件，将谓词条件应用于中间列表上，过滤掉不符合条件的节点
            if operation.pred is not None:
                pathOpList = operation.pred.attr
                for i in range(len(nextList) - 1, -1, -1):
                    predResult = execute(nextList[i], pathOpList)
                    if len(predResult) != 1 or (isinstance(predResult[0], node) and predResult[0].mode != "data"):
                        nextList.remove(nextList[i])
                    lhs = predResult[0]
                    if isinstance(lhs, node):
                        lhs = lhs.data if isinstance(lhs.data, str) == False else "\"" + lhs.data + "\""
                    rhs = operation.pred.val if isinstance(operation.pred.val, str) == False else "\"" + operation.pred.val + "\""
                    if eval(str(lhs) + operation.pred.op + str(rhs)) == False:
                        nextList.remove(nextList[i])
            nodeList = nextList
        return nodeList
    except:
        print("Execute error!")
        return

def print_data(nodeList):
    if nodeList is None or len(nodeList) == 0:
        print()
        return
    for item in nodeList:
        if isinstance(item, node):
            print(item.to_string(True))
        else:
            print(item)

if __name__ == "__main__":
    f = open("./data.txt", "r", encoding='UTF-8')
    jsonStr = f.read()
    rootNode = node(None, json.loads(jsonStr), None)
    operationList = jsonpathParser.parser(sys.argv[1])
    result = execute(rootNode, operationList)
    print_data(result)