import { IsString, IsNotEmpty, IsOptional } from "class-validator";

export class JoinRoomDto {
  @IsString()
  @IsNotEmpty({ message: "Room name is required" })
  room_name: string;

  @IsOptional()
  @IsString()
  password?: string;
}
