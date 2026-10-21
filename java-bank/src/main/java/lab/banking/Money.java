package lab.banking;

import java.math.BigDecimal;
import java.math.RoundingMode;

public final class Money {
    private Money() {}
    public static long cents(String value) {
        try {
            if (value == null || value.length() > 30) throw new IllegalArgumentException();
            BigDecimal amount = new BigDecimal(value);
            if (amount.signum() <= 0 || amount.compareTo(new BigDecimal("1000000")) > 0)
                throw new IllegalArgumentException();
            return amount.setScale(2, RoundingMode.UNNECESSARY).movePointRight(2).longValueExact();
        } catch (IllegalArgumentException | ArithmeticException e) {
            throw new BankError(422, "Importe inválido: mayor a cero, máximo 1000000 y dos decimales");
        }
    }
    public static String format(long cents) { return BigDecimal.valueOf(cents, 2).toPlainString(); }
}
