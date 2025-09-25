/* eslint-disable @typescript-eslint/no-unsafe-call */
import { IsNotEmpty } from "class-validator";

export class RefreshUserTokensDto {
  @IsNotEmpty({ message: "User ID is required" })
  readonly userID: string;

  @IsNotEmpty({ message: "Refresh token is required" })
  readonly refreshToken: string;
}
