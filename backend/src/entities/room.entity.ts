import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  Generated,
  ManyToMany,
  JoinTable,
  OneToMany,
} from "typeorm";
import { User } from "./user.entity";
import { Message } from "./message.entity";

@Entity()
export class Room {
  @PrimaryGeneratedColumn()
  @Generated("uuid")
  id: string | undefined;

  @Column({ unique: true })
  name: string;

  @Column({ default: false })
  private: boolean;

  @Column({ nullable: true })
  password: string;

  @Column()
  createdAt: Date;

  @Column()
  createdBy: string; // User ID who created the room

  @ManyToMany(() => User, { eager: false })
  @JoinTable({ name: "room_users" })
  users: User[];

  @OneToMany(() => Message, (message) => message.room, { eager: false })
  messages: Message[];
}
