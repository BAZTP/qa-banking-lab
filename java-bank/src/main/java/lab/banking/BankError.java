package lab.banking;

public class BankError extends RuntimeException {
    final int status;
    public BankError(int status, String message) { super(message); this.status = status; }
}
