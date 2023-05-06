import datetime

offset_transactionID = 0
offset_flags = 4
offset_query = 24
offset_len_name = 26


class Header():
    transactionID = None
    flags = None
    questions = None
    answers = None
    athority = None
    additional = None

    def __init__(self, data):
        self.transactionID = data[:4]
        self.flags = data[4:8]
        self.questions = data[8:12]
        self.answers = data[12:16]
        self.athority = data[16:20]
        self.additional = data[20:24]


class Query(Header):
    name = None
    type = None
    clss = None
    __dataQuery = None

    def __init__(self, data: str):
        super().__init__(data)
        self.__dataQuery = data
        self.get_name()
        self.get_type()
        self.get_clss()

    def get_id(self): # unused
        self.transactionID = self.__dataQuery[:4]

    def get_flags(self): # unused
        self.flags = self.__dataQuery[4:8]

    def get_name(self):
        res = ""
        len_name = int(self.__dataQuery[offset_query:offset_query + 2])
        offset = offset_query + len_name * 2 + 1
        for i in range(offset_query + 2, offset, 2):
            res += self.__dataQuery[i:i + 2]
        res = bytes.fromhex(res).decode('866')
        res += "."
        d = ""
        offset += 1
        domain = int(self.__dataQuery[offset:offset + 2])
        offset += 2
        for i in range(offset, (offset + domain * 2), 2):
            d += self.__dataQuery[i:i + 2]
        d = bytes.fromhex(d).decode('866')
        self.name = res + d
        self.__len_name_offset = offset_query + domain * 2 + len_name * 2 + 4 + 2

    def get_type(self):
        self.type = self.__dataQuery[self.__len_name_offset:self.__len_name_offset + 4]

    def get_clss(self):
        self.len_query = self.__len_name_offset + 8
        self.clss = self.__dataQuery[self.__len_name_offset + 4:self.__len_name_offset + 8]


class Response(Query):
    response = None
    __offset = None
    res = None

    def __init__(self, data: str):
        super().__init__(data)
        self.__data = data
        self.__offset = self.len_query
        self.get_ans()
        # self.response = data[8:]

    def get_ans(self):
        offset = 0
        data = self.__data[self.len_query:]
        ans = int(self.answers, 16)
        athr = int(self.athority, 16)
        add = int(self.additional, 16)
        res = {}
        res["ans"] = []
        res["athr"] = []
        res["add"] = []

        while ans:
            start = offset
            offset += 12
            ddd = data[offset: offset + 8]
            ttl = int(ddd, 16)
            offset += 8
            dlen = data[offset: offset + 4]
            offset += 4
            offset += int(dlen, 16) * 2
            res["ans"].append([int(datetime.datetime.now().timestamp()) + ttl, data[start: offset]])
            ans -= 1

        while athr:
            start = offset
            offset += 12
            ttl = int(data[offset: offset + 8], 16)
            offset += 8
            dlen = data[offset: offset + 4]
            offset += 4
            offset += int(dlen, 16) * 2
            res["add"].append([int(datetime.datetime.now().timestamp()) + ttl, data[start: offset]])
            athr -= 1

        while add:
            start = offset
            offset += 12
            ttl = int(data[offset: offset + 8], 16)
            offset += 8
            dlen = data[offset: offset + 4]
            offset += 4
            offset += int(dlen, 16) * 2
            res["add"].append([int(datetime.datetime.now().timestamp()) + ttl, data[start: offset]])
            add -= 1

        self.res = res

    def build(self):
        res = "8500"
        res += self.questions
        res += "0" * (4 - len(str(len(self.res["ans"])))) + str(len(self.res["ans"]))
        res += "0" * (4 - len(str(len(self.res["athr"])))) + str(len(self.res["athr"]))
        res += "0" * (4 - len(str(len(self.res["add"])))) + str(len(self.res["add"]))
        res += self.__data[24:self.len_query]
        for i in self.res["ans"]:
            res += i[1]
        for i in self.res["athr"]:
            res += i[1]
        for i in self.res["add"]:
            res += i[1]
        return res

    def filter(self):
        cur = int(datetime.datetime.now().timestamp())
        for i in self.res:
            for j in self.res[i]:
                if j[0] - cur <= 0:
                    return True
        return False

def main():
    pass
    # d = load_cache()
    # print(d[1].build())
    data1 = "002b818000010004000000000679616e6465780272750000010001c00c00010001000000bb000405ffff46c00c00010001000000bb00044d58373cc00c00010001000000bb00044d583758c00c00010001000000bb000405ffff4d"
    r1 = Response(data1)
    # data2 = "0007818000010002000000030679616e6465780272750000020001c00c00020001000051810006036e7332c00cc00c00020001000051810006036e7331c00cc0390001000100014f900004d5b4c101c027000100010000945300045d9e8601c039001c000100000dd600102a0206b8000000000000000000000001"
    # r2 = ResponseParser(data2)
    # dump_cache([r1, r2])
    print(r1.build())
    # q = QueryParser(data)
    # print(r.transactionID, r.flags, r.name, r.type, r.clss, r.response)
    # h = HeaderParser(data)
    # print(h.transactionID, h.flags, h.questions, h.answers, h.athority, h.additional)


if __name__ == "__main__":
    main()
