# pcap-read

读 pcap 抓包文件：按字节序与时间单位解析全局头，建立按包定位的索引。只用 Python 标准库。

```
python3 -m unittest discover -s tests
python3 -m pcapread --sample=be
python3 -m pcapread --sample=nano
python3 -m pcapread --sample=snaplen
python3 -m pcapread --sample=trunc
python3 -m pcapread --sample=work
```

## 口径

- **字节序**：全局头前 4 字节决定整份文件的字节序，后续所有多字节字段都按它读。
- **时间单位**：微秒与纳秒两种魔数都要认，认出来的单位记在索引上。
- **抓取上限**：单包长度超过全局头声明的上限时，该记录及其之后的记录都不再收。
- **截断**：记录头声明的包长超出文件剩余字节时，只收下已经完整的记录。
- **定位**：索引建成后按序号取包，不应重新遍历前面的记录。

## 不变量

- 索引里的记录数与文件里完整且不超上限的记录数一致。
- 任一记录的包长不超过抓取上限，且数据都在文件内。
- `scanned` 不随包数平方级放大：两千个包逐个取一遍的 `scanned` 不超过 6000。

## 输出契约

场景打印一行 JSON，键随场景而定；解析失败打印 `{"error": <原因>}`。
`--sample=work` 打印 `{"packets": N, "scanned": N}`。
