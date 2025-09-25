import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";
import { ValidationPipe } from "@nestjs/common";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Enable CORS for all origins (configure as needed)
  app.enableCors({
    origin: true, // Allow all origins for development
    credentials: true,
  });

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // strips unknown properties
      forbidNonWhitelisted: true, // throws if extra props provided
      transform: true, // auto-transforms types (e.g., string -> number)
    }),
  );

  const port = process.env.PORT || 5200;
  await app.listen(port, "0.0.0.0");
  console.log(`Server running on http://0.0.0.0:${port}`);
}
void bootstrap();
