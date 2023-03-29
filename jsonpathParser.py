class condition:
    def __init__(self, attr, op, val) -> None:
        self.attr = attr
        self.op = op
        self.val = val.strip("\"") if val[0] == "\"" else int(val) if val.find(".") == -1 else float(val)

class operation:
    def __init__(self, axis, attr, pred, aggr) -> None:
        self.axis = axis  # [child, descendant, descendant-or-self, parent, ancestor, ancestor-or-self]
        self.attr = attr  # Extra support: node(), text()
        self.pred = pred  # ["!=", "<=", ">=", "=", "<", ">"]
        self.aggr = aggr  # [count, sum, avg, max, min]

def parseCond(predStr: str) -> condition:
    opList = ["!=", "<=", ">=", "==", "<", ">"]
    for op in opList:
        idx = predStr.find(op)
        if idx != -1:
            return condition(parser("/" + predStr[0: idx]), op, predStr[idx + len(op): ])
    return None

def parser(queryStr: str) -> list[operation]:
    resultList, startIdx, nextIdx, predIdx = [], 1, -1, -1
    headAggr = None
    if queryStr[0] != '/': # 查询的整体有聚合
        commaIdx = queryStr.find("(") + 1
        headAggr = queryStr[0: commaIdx - 1]
        queryStr = queryStr[commaIdx: -1]
    
    queryStr += '/'

    while startIdx != len(queryStr):
        commaIdx, nextIdx, leftPredIdx, rightPredIdx, axisIdx = queryStr.find('(', startIdx), queryStr.find('/', startIdx), queryStr.find('[', startIdx), queryStr.find(']', startIdx), queryStr.find(':', startIdx)
        pathStart, pathEnd, aggr, pred = startIdx, nextIdx, None, None
        if commaIdx != -1 and commaIdx < axisIdx:  # 这一级有聚合
            aggr = queryStr[startIdx: commaIdx]
            pathStart = commaIdx + 1
            pathEnd = queryStr.find(')', pathStart)
            nextIdx = pathEnd + 1
        if leftPredIdx != -1 and nextIdx > leftPredIdx: # 这一级有谓词
            pred = parseCond(queryStr[leftPredIdx + 1: rightPredIdx])
            pathEnd = leftPredIdx
            if aggr is None:
                nextIdx = rightPredIdx + 1
        axis, attr = queryStr[pathStart: axisIdx], queryStr[axisIdx + 2: pathEnd]
        # print(pathStart, pathEnd, axis, attr)
        resultList.append(operation(axis, attr, pred, None))
        if aggr is not None:
            resultList.append(operation(None, None, None, aggr))
        startIdx = nextIdx + 1
    
    if headAggr is not None:
        resultList.append(operation(None, None, None, headAggr))
    return resultList

if __name__ == "__main__":
    operationList = parser("count(/child::addresses)")
    for operation in operationList:
        print(operation.axis, operation.attr, operation.aggr, end = " ")
        if operation.pred is not None:
            print("\"", end = "")
            for suboper in operation.pred.attr:
                print(suboper.axis, suboper.attr, suboper.aggr, "/ ", end = "")
            print(operation.pred.op, operation.pred.val, end = " ")
            print("\"")
        else:
            print(None)
