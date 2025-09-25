import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  Generated,
  ManyToOne,
  JoinColumn,
} from "typeorm";
import { User } from "./user.entity";
import { Room } from "./room.entity";

@Entity()
export class Message {
  @PrimaryGeneratedColumn()
  @Generated("uuid")
  id: string | undefined;

  @Column("text")
  content: string;

  @Column()
  timestamp: Date;

  @ManyToOne(() => User, { eager: true })
  @JoinColumn({ name: "userId" })
  user: User;

  @Column()
  userId: string;

  @ManyToOne(() => Room, (room) => room.messages, { eager: false })
  @JoinColumn({ name: "roomId" })
  room: Room;

  @Column()
  roomId: string;

  @Column()
  username: string; // Denormalized for quick access
}
