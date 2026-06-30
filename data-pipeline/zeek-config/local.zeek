# SecOpsAI Zeek Configuration
@load base/protocols/conn
@load base/protocols/dns
@load base/protocols/http
@load base/protocols/ssl
@load base/frameworks/notice

redef LogAscii::use_json = T;
