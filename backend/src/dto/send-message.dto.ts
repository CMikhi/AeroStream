import { IsString, IsNotEmpty } from "class-validator";

export class SendMessageDto {
  @IsString()
  @IsNotEmpty({ message: "Room name is required" })
  room_name: string;

  @IsString()
  @IsNotEmpty({ message: "Message content is required" })
  message: string;
}
