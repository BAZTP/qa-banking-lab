package lab.banking;

import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.boot.WebApplicationType;
import org.springframework.boot.builder.SpringApplicationBuilder;
import static org.junit.jupiter.api.Assertions.*;

class PersistenceTest {
    @TempDir Path temporary;
    @Test void restartDoesNotReseedOrLoseOperations() {
        String url = "--spring.datasource.url=jdbc:h2:file:" + temporary.resolve("bank");
        for (int iteration = 0; iteration < 2; iteration++) {
            try (var context = new SpringApplicationBuilder(BankApplication.class)
                    .web(WebApplicationType.NONE).run(url)) {
                BankService service = context.getBean(BankService.class);
                if (iteration == 0) service.withdraw("ana", "LAB-ANA-01", "50.00");
                assertEquals("950.00", service.accounts("ana").getFirst().balance());
                assertEquals(1, service.history("ana").size());
            }
        }
    }
}
