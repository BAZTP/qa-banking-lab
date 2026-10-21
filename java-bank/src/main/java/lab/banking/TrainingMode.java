package lab.banking;

import java.util.Arrays;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

@Component
public class TrainingMode {
    private final boolean enabled;
    public TrainingMode(@Value("${lab.training-bugs:false}") boolean requested, Environment environment) {
        boolean isolated = Arrays.asList(environment.getActiveProfiles()).contains("training");
        if (requested && !isolated)
            throw new IllegalStateException("Los bugs requieren el perfil training y su base aislada");
        if (requested && !environment.getProperty("spring.datasource.url", "").startsWith("jdbc:h2:mem:"))
            throw new IllegalStateException("Los bugs solo pueden usar una base H2 en memoria");
        enabled = requested;
    }
    public boolean enabled() { return enabled; }
}
