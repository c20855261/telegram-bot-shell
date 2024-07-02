# telegram-bot-shell
2024-03-06
app-v1

新增分割傳遞消息，解決telegram消息過長無法顯示問題

新增腳本向後繼續傳遞變量，例:test.sh $1 $2

---
2024-06-28
app-v2

1. 新增 可輸入多個關鍵字

2. 判斷輸入關鍵字是直接執行還是繼續向後傳遞變量
---
2024-07-01
app-v3

1. 新增update_json按鈕，應答式回應 Y/N 確認是否繼續執行。

---
2024-07-02
app-v4

1. 增加 ParseMode，讓 telegram bot 輸出 parse_mode=ParseMode.HTML。
2. 調整command變量，讓 bot api 可使用無序方式輸出。
3. bug fix 新增 當輸入命令時，遠端沒有對應腳本判斷
