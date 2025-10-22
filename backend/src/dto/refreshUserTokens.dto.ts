import { IsNotEmpty, IsString } from "class-validator";

export class RefreshUserTokensDto {
  @IsNotEmpty({ message: "Refresh token is required" })
  @IsString({ message: "Refresh token must be a string" })
  readonly refresh_token: string;
}
