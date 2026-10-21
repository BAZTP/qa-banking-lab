package lab.banking;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;
import static org.junit.jupiter.api.Assertions.*;

class MoneyTest {
    @ParameterizedTest @CsvSource({"0.01,1", "10.25,1025", "1000,100000", "1000000,100000000"})
    void convertsWithoutRounding(String amount, long cents) {
        assertEquals(cents, Money.cents(amount));
        assertEquals(cents, Money.cents(Money.format(cents)));
    }
    @ParameterizedTest @ValueSource(strings={"0", "-1", "1.001", "NaN", "Infinity", "1000000.01", "abc", ""})
    void rejectsInvalidAmounts(String amount) { assertThrows(BankError.class, () -> Money.cents(amount)); }
}
