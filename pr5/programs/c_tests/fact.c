int fact(int n) {
    int f;

    if (n <= 1) {
        return 1;
    }

    f = n * fact(n - 1);
    return f;
}

int main() {
    int n;
    n = fact(5);
    return n;
}
