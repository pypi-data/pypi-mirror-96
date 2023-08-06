pub struct Error(pub String);

impl<T: std::fmt::Display> From<T> for Error {
    fn from(src: T) -> Error {
        Error(format!("{}", src))
    }
}
impl std::fmt::Debug for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        f.pad(self.0.as_str())
    }
}
