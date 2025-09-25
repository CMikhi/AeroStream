import { Entity, Column, PrimaryGeneratedColumn, Generated } from "typeorm";

@Entity()
export class User {
  @PrimaryGeneratedColumn()
  @Generated("uuid")
  id: string | undefined;

  @Column({ unique: true })
  username: string;

  @Column()
  createdAt: Date;

  @Column()
  password: string;

  @Column({ default: "user" })
  role: string;

  @Column({ nullable: true })
  refreshTokenHash: string;
}
