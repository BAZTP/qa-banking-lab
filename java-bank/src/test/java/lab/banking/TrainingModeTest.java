package lab.banking;

import org.junit.jupiter.api.Test;
import org.springframework.mock.env.MockEnvironment;
import static org.junit.jupiter.api.Assertions.*;

class TrainingModeTest {
    @Test void rejectsBugsWithoutTrainingProfile() {
        assertThrows(IllegalStateException.class, () -> new TrainingMode(true, new MockEnvironment()));
    }
    @Test void rejectsBugsWithPersistentDatabase() {
        MockEnvironment env = new MockEnvironment().withProperty("spring.datasource.url", "jdbc:h2:file:./data/normal");
        env.setActiveProfiles("training");
        assertThrows(IllegalStateException.class, () -> new TrainingMode(true, env));
    }
}
