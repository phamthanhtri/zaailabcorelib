namespace cpp something

struct TResult {
    1: i32 errorCode,
    2: optional string  message,
}     


service Ping {
  TResult pong(1: optional i32 value),
}