from prometheus_client import Counter, Histogram

http_requests_total = Counter("http_requests_total","HTTP requests",["method","path","status"])
okx_requests_total  = Counter("okx_requests_total","OKX requests",["method","path","status"])
http_latency = Histogram("http_request_duration_seconds","HTTP latency",["method","path"])
okx_latency  = Histogram("okx_request_duration_seconds","OKX latency",["method","path"])
ai_decision_total = Counter("ai_decision_total","AI decisions",["action","reason"])
