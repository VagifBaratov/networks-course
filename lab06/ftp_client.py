#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ftplib
import os
import sys
from typing import List, Tuple

class FTPClient:
    def __init__(self, host: str = '127.0.0.1', port: int = 21, 
                 username: str = 'anonymous', password: str = ''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ftp = None
        self.connected = False
    
    def connect(self) -> bool:
        try:
            self.ftp = ftplib.FTP()
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.username, self.password)
            self.connected = True
            print(f"Подключено к {self.host}:{self.port}")
            print(f"Пользователь: {self.username}")

            welcome = self.ftp.getwelcome()
            if welcome:
                print(f"{welcome}")
            return True
        except ftplib.all_errors as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def disconnect(self):
        if self.ftp and self.connected:
            try:
                self.ftp.quit()
                print("\nОтключено от сервера")
            except:
                self.ftp.close()
            finally:
                self.connected = False
    
    def list_files(self, path: str = '.') -> List[Tuple[str, dict]]:
        try:
            files = []
            self.ftp.dir(path, lambda line: files.append(line))
            
            if not files:
                return []
            
            print(f"{'Тип':<6} {'Имя':<30} {'Размер':<10}")
            print(f"{'-'*60}")
            
            parsed_files = []
            for line in files:
                parts = line.split()
                if len(parts) < 9:
                    continue
                
                is_dir = line.startswith('d')
                file_type = "DIR" if is_dir else "FILE"
                name = ' '.join(parts[8:])
                size = parts[4] if not is_dir else "-"
                
                print(f"{file_type:<6} {name:<30} {size:<10}")
                parsed_files.append((name, {'is_dir': is_dir, 'size': size}))
            
            return parsed_files
            
        except ftplib.error_perm as e:
            print(f"Ошибка: {e}")
            return []
    
    def change_dir(self, directory: str) -> bool:
        try:
            self.ftp.cwd(directory)
            return True
        except ftplib.error_perm as e:
            print(f"Не удалось перейти в '{directory}': {e}")
            return False
    
    def get_current_dir(self) -> str:
        try:
            return self.ftp.pwd()
        except:
            return "Неизвестно"
    
    def download_file(self, remote_file: str, local_file: str = None) -> bool:
        if local_file is None:
            local_file = remote_file
        
        try:
            self.ftp.size(remote_file)
        except ftplib.error_perm:
            print(f"'{remote_file}' не доступен, либо не является файлом")
            return False
        
        try:
            with open(local_file, 'wb') as f:
                self.ftp.retrbinary(f'RETR {remote_file}', f.write)
            print(f"Файл скачан: {remote_file} -> {local_file}")
            return True
        except Exception as e:
            print(f"Ошибка при скачивании: {e}")
            return False
    
    def upload_file(self, local_file: str, remote_file: str = None) -> bool:
        if not os.path.exists(local_file):
            print(f"Локальный файл не найден: {local_file}")
            return False
        
        if os.path.isdir(local_file):
            print(f"'{local_file}' это директория, а не файл")
            return False
        
        if remote_file is None:
            remote_file = os.path.basename(local_file)
        
        try:
            with open(local_file, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_file}', f)
            print(f"Файл загружен: {local_file} -> {remote_file}")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке: {e}")
            return False
    
    def delete_file(self, filename: str) -> bool:
        try:
            self.ftp.delete(filename)
            print(f"Файл удален: {filename}")
            return True
        except ftplib.error_perm as e:
            print(f"Не удалось удалить '{filename}': {e}")
            return False
    
    def make_directory(self, dirname: str) -> bool:
        try:
            self.ftp.mkd(dirname)
            return True
        except ftplib.error_perm as e:
            print(f"Не удалось создать директорию '{dirname}': {e}")
            return False
    
    def remove_directory(self, dirname: str) -> bool:
        try:
            if not self._is_directory_empty(dirname):
                print(f"Директория должна быть пуста!")
                return False
            
            self.ftp.rmd(dirname)
            return True
        except ftplib.error_perm as e:
            print(f"Не удалось удалить директорию '{dirname}': {e}")
            return False
    
    def _is_directory_empty(self, dirname: str) -> bool:
        current_dir = self.ftp.pwd()

        self.ftp.cwd(dirname)

        items = self.ftp.nlst()
        filtered_items = [item for item in items if item not in ('.', '..')]

        self.ftp.cwd(current_dir)
        return len(filtered_items) == 0
    
    def get_file_size(self, filename: str) -> int:
        try:
            return self.ftp.size(filename)
        except:
            return -1


def print_help():
    print("""
            ДОСТУПНЫЕ КОМАНДЫ                         
    ls, dir                    - показать содержимое текущей директории 
    cd <dir>                   - перейти в директорию                   
    get <file> <local_name>    - скачать файл с сервера                 
    put <file> <remote_name>   - загрузить файл на сервер               
    delete <file>              - удалить файл на сервере                
    mkdir <dir>                - создать директорию                     
    rmdir <dir>                - удалить директорию                     
    exit                       - выйти из программы                     
    """)


def main():

    
    host = input("Введите адрес FTP сервера [127.0.0.1]: ").strip()
    if not host:
        host = '127.0.0.1'
    
    port_str = input("Введите порт [21]: ").strip()
    port = int(port_str) if port_str else 21
    
    username = input("Введите имя пользователя: ").strip()
    if not username:
        username = 'anonym'
    
    password = input("Введите пароль: ").strip()
    
    client = FTPClient(host, port, username, password)
    
    if not client.connect():
        print("Не удалось подключиться к серверу.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Клиент готов к работе. Введите 'help' для списка команд.")
    print("=" * 60)
    
    while True:
        try:
            current_dir = client.get_current_dir()
            command = input(f"ftp:{current_dir}> ").strip()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            args = parts[1:]
            
            if cmd == 'exit':
                break
            
            elif cmd == 'help':
                print_help()
            
            elif cmd == 'ls':
                path = args[0] if args else '.'
                client.list_files(path)
            
            elif cmd == 'cd':
                if not args:
                    print("Укажите директорию")
                else:
                    client.change_dir(args[0])
            
            elif cmd == 'get':
                if not args:
                    print("Укажите имя файла для скачивания")
                else:
                    local_name = args[1] if len(args) > 1 else None

                    client.download_file(args[0], local_name)
            
            elif cmd == 'put':
                if not args:
                    print("Укажите имя локального файла")
                else:
                    remote_name = args[1] if len(args) > 1 else None
                    client.upload_file(args[0], remote_name)
            
            elif cmd == 'delete':
                if not args:
                    print("Укажите имя файла для удаления")
                else:
                    client.delete_file(args[0])
            
            elif cmd == 'mkdir':
                if not args:
                    print("Укажите имя директории")
                else:
                    client.make_directory(args[0])
            
            elif cmd == 'rmdir':
                if not args:
                    print("Укажите имя директории")
                else:
                    client.remove_directory(args[0])
            
            else:
                print(f"Неизвестная команда: {cmd}. Введите 'help' для списка команд.")
        
        except KeyboardInterrupt:
            print("\n\nПрерывание работы...")
            break
        except EOFError:
            break
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
    
    client.disconnect()
    print("Программа завершена.")


if __name__ == "__main__":
    main()