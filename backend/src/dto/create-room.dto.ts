import { IsString, IsNotEmpty, IsOptional, IsBoolean } from "class-validator";

export class CreateRoomDto {
  @IsString()
  @IsNotEmpty({ message: "Room name is required" })
  room_name: string;

  @IsOptional()
  @IsBoolean()
  private?: boolean;

  @IsOptional()
  @IsString()
  password?: string;
}
