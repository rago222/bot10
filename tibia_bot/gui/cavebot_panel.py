"""
Cavebot Panel - Painel de configuração e controle do cavebot
Interface para criar, editar e executar scripts de navegação
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from pathlib import Path

class CavebotPanel:
    """Painel do cavebot"""
    
    def __init__(self, parent, bot_manager):
        self.parent = parent
        self.bot_manager = bot_manager
        
        self.frame = ttk.Frame(parent, padding="10")
        self.create_widgets()
        
        # Estado do cavebot
        self.current_script_path = ""
        self.waypoints = []
        self.recording = False
    
    def create_widgets(self):
        """Cria widgets do painel do cavebot"""
        # Controles principais
        controls_frame = ttk.LabelFrame(self.frame, text="Controles", padding="10")
        controls_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botões de controle
        ttk.Button(controls_frame, text="Iniciar Cavebot", 
                  command=self.start_cavebot).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(controls_frame, text="Parar Cavebot", 
                  command=self.stop_cavebot).grid(row=0, column=1, padx=5)
        ttk.Button(controls_frame, text="Pausar", 
                  command=self.pause_cavebot).grid(row=0, column=2, padx=(5, 0))
        
        # Status do cavebot
        status_frame = ttk.Frame(controls_frame)
        status_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, text="Parado", foreground="red")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(status_frame, text="Waypoint:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.waypoint_label = ttk.Label(status_frame, text="0/0")
        self.waypoint_label.grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
        # Scripts
        script_frame = ttk.LabelFrame(self.frame, text="Scripts", padding="10")
        script_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Lista de scripts
        scripts_list_frame = ttk.Frame(script_frame)
        scripts_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.scripts_listbox = tk.Listbox(scripts_list_frame, height=8)
        scripts_scrollbar = ttk.Scrollbar(scripts_list_frame, orient=tk.VERTICAL, 
                                         command=self.scripts_listbox.yview)
        self.scripts_listbox.configure(yscrollcommand=scripts_scrollbar.set)
        
        self.scripts_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scripts_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        scripts_list_frame.columnconfigure(0, weight=1)
        scripts_list_frame.rowconfigure(0, weight=1)
        
        # Botões de script
        script_buttons_frame = ttk.Frame(script_frame)
        script_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(script_buttons_frame, text="Carregar", 
                  command=self.load_script).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(script_buttons_frame, text="Salvar", 
                  command=self.save_script).grid(row=0, column=1, padx=5)
        ttk.Button(script_buttons_frame, text="Novo", 
                  command=self.new_script).grid(row=0, column=2, padx=5)
        ttk.Button(script_buttons_frame, text="Excluir", 
                  command=self.delete_script).grid(row=0, column=3, padx=(5, 0))
        
        # Editor de waypoints
        editor_frame = ttk.LabelFrame(self.frame, text="Editor de Waypoints", padding="10")
        editor_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Lista de waypoints
        waypoints_list_frame = ttk.Frame(editor_frame)
        waypoints_list_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Treeview para waypoints
        columns = ('Tipo', 'X', 'Y', 'Ação')
        self.waypoints_tree = ttk.Treeview(waypoints_list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.waypoints_tree.heading(col, text=col)
            self.waypoints_tree.column(col, width=80)
        
        waypoints_scrollbar = ttk.Scrollbar(waypoints_list_frame, orient=tk.VERTICAL, 
                                           command=self.waypoints_tree.yview)
        self.waypoints_tree.configure(yscrollcommand=waypoints_scrollbar.set)
        
        self.waypoints_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        waypoints_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        waypoints_list_frame.columnconfigure(0, weight=1)
        waypoints_list_frame.rowconfigure(0, weight=1)
        
        # Controles de waypoint
        waypoint_controls_frame = ttk.Frame(editor_frame)
        waypoint_controls_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Formulário de waypoint
        form_frame = ttk.LabelFrame(waypoint_controls_frame, text="Adicionar Waypoint", padding="5")
        form_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(form_frame, text="Tipo:").grid(row=0, column=0, sticky=tk.W)
        self.waypoint_type_var = tk.StringVar(value="walk")
        type_combo = ttk.Combobox(form_frame, textvariable=self.waypoint_type_var, width=12,
                                 values=["walk", "attack", "stairs", "hole", "rope", "wait"])
        type_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 10))
        
        ttk.Label(form_frame, text="X:").grid(row=0, column=2, sticky=tk.W)
        self.waypoint_x_var = tk.IntVar()
        ttk.Entry(form_frame, textvariable=self.waypoint_x_var, width=8).grid(row=0, column=3, sticky=tk.W, padx=(5, 10))
        
        ttk.Label(form_frame, text="Y:").grid(row=0, column=4, sticky=tk.W)
        self.waypoint_y_var = tk.IntVar()
        ttk.Entry(form_frame, textvariable=self.waypoint_y_var, width=8).grid(row=0, column=5, sticky=tk.W, padx=(5, 10))
        
        ttk.Label(form_frame, text="Ação:").grid(row=1, column=0, sticky=tk.W)
        self.waypoint_action_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.waypoint_action_var, width=20).grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=(5, 10))
        
        ttk.Label(form_frame, text="Delay (s):").grid(row=1, column=3, sticky=tk.W)
        self.waypoint_delay_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.waypoint_delay_var, width=8).grid(row=1, column=4, sticky=tk.W, padx=(5, 0))
        
        # Botões de waypoint
        wp_buttons_frame = ttk.Frame(waypoint_controls_frame)
        wp_buttons_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        ttk.Button(wp_buttons_frame, text="Adicionar", 
                  command=self.add_waypoint).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(wp_buttons_frame, text="Remover", 
                  command=self.remove_waypoint).grid(row=0, column=1, padx=5)
        ttk.Button(wp_buttons_frame, text="Editar", 
                  command=self.edit_waypoint).grid(row=0, column=2, padx=5)
        ttk.Button(wp_buttons_frame, text="Limpar Todos", 
                  command=self.clear_waypoints).grid(row=0, column=3, padx=(5, 0))
        
        # Ferramentas avançadas
        tools_frame = ttk.LabelFrame(self.frame, text="Ferramentas", padding="10")
        tools_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Gravação de waypoints
        record_frame = ttk.Frame(tools_frame)
        record_frame.grid(row=0, column=0, sticky=tk.W)
        
        self.record_button = ttk.Button(record_frame, text="Iniciar Gravação", 
                                       command=self.toggle_recording)
        self.record_button.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Label(record_frame, text="Status:").grid(row=0, column=1, sticky=tk.W)
        self.record_status_label = ttk.Label(record_frame, text="Parado")
        self.record_status_label.grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        
        # Configurações do cavebot
        config_frame = ttk.Frame(tools_frame)
        config_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Label(config_frame, text="Alcance de ataque:").grid(row=0, column=0, sticky=tk.W)
        self.attack_range_var = tk.IntVar(value=5)
        ttk.Spinbox(config_frame, from_=1, to=10, width=5, 
                   textvariable=self.attack_range_var).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Configurar expansão
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)
        script_frame.columnconfigure(0, weight=1)
        script_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)
        
        # Carregar scripts disponíveis
        self.refresh_scripts_list()
    
    def start_cavebot(self):
        """Inicia o cavebot"""
        try:
            if not self.waypoints:
                messagebox.showerror("Erro", "Nenhum waypoint configurado!")
                return
            
            # Carregar waypoints no módulo cavebot
            cavebot_module = self.bot_manager.modules['cavebot']
            cavebot_module.waypoints = self.waypoints.copy()
            cavebot_module.script_loaded = True
            
            # Iniciar cavebot
            cavebot_module.start_cavebot()
            
            self.status_label.config(text="Executando", foreground="green")
            messagebox.showinfo("Sucesso", "Cavebot iniciado!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar cavebot: {e}")
    
    def stop_cavebot(self):
        """Para o cavebot"""
        try:
            cavebot_module = self.bot_manager.modules['cavebot']
            cavebot_module.stop_cavebot()
            
            self.status_label.config(text="Parado", foreground="red")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao parar cavebot: {e}")
    
    def pause_cavebot(self):
        """Pausa/despausa o cavebot"""
        try:
            # Implementar lógica de pausa
            messagebox.showinfo("Info", "Função de pausa será implementada em breve!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao pausar cavebot: {e}")
    
    def load_script(self):
        """Carrega script de arquivo"""
        try:
            filename = filedialog.askopenfilename(
                title="Carregar Script do Cavebot",
                initialdir="scripts",
                filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
            )
            
            if filename:
                cavebot_module = self.bot_manager.modules['cavebot']
                if cavebot_module.load_script(filename):
                    self.waypoints = cavebot_module.waypoints.copy()
                    self.current_script_path = filename
                    self.refresh_waypoints_list()
                    messagebox.showinfo("Sucesso", "Script carregado com sucesso!")
                else:
                    messagebox.showerror("Erro", "Erro ao carregar script!")
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar script: {e}")
    
    def save_script(self):
        """Salva script atual"""
        try:
            if not self.waypoints:
                messagebox.showerror("Erro", "Nenhum waypoint para salvar!")
                return
            
            filename = filedialog.asksaveasfilename(
                title="Salvar Script do Cavebot",
                initialdir="scripts",
                defaultextension=".json",
                filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
            )
            
            if filename:
                # Criar estrutura do script
                script_data = {
                    'name': Path(filename).stem,
                    'created': tk.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'waypoints': []
                }
                
                for wp in self.waypoints:
                    wp_data = {
                        'x': wp.x,
                        'y': wp.y,
                        'type': wp.type.value,
                        'action': wp.action,
                        'delay': wp.delay
                    }
                    script_data['waypoints'].append(wp_data)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(script_data, f, indent=2, ensure_ascii=False)
                
                self.current_script_path = filename
                self.refresh_scripts_list()
                messagebox.showinfo("Sucesso", "Script salvo com sucesso!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar script: {e}")
    
    def new_script(self):
        """Cria novo script"""
        try:
            if self.waypoints:
                if not messagebox.askyesno("Confirmar", "Deseja descartar o script atual?"):
                    return
            
            self.waypoints.clear()
            self.current_script_path = ""
            self.refresh_waypoints_list()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar novo script: {e}")
    
    def delete_script(self):
        """Exclui script selecionado"""
        try:
            selection = self.scripts_listbox.curselection()
            if not selection:
                messagebox.showerror("Erro", "Selecione um script para excluir!")
                return
            
            script_name = self.scripts_listbox.get(selection[0])
            
            if messagebox.askyesno("Confirmar", f"Deseja excluir o script '{script_name}'?"):
                script_path = Path("scripts") / f"{script_name}.json"
                if script_path.exists():
                    script_path.unlink()
                    self.refresh_scripts_list()
                    messagebox.showinfo("Sucesso", "Script excluído!")
                else:
                    messagebox.showerror("Erro", "Arquivo do script não encontrado!")
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir script: {e}")
    
    def add_waypoint(self):
        """Adiciona waypoint à lista"""
        try:
            from modules.cavebot import Waypoint, WaypointType
            
            # Criar waypoint
            waypoint = Waypoint(
                x=self.waypoint_x_var.get(),
                y=self.waypoint_y_var.get(),
                type=WaypointType(self.waypoint_type_var.get()),
                action=self.waypoint_action_var.get(),
                delay=self.waypoint_delay_var.get()
            )
            
            self.waypoints.append(waypoint)
            self.refresh_waypoints_list()
            
            # Limpar formulário
            self.waypoint_x_var.set(0)
            self.waypoint_y_var.set(0)
            self.waypoint_action_var.set("")
            self.waypoint_delay_var.set(0.0)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar waypoint: {e}")
    
    def remove_waypoint(self):
        """Remove waypoint selecionado"""
        try:
            selection = self.waypoints_tree.selection()
            if not selection:
                messagebox.showerror("Erro", "Selecione um waypoint para remover!")
                return
            
            # Obter índice do item selecionado
            item = selection[0]
            index = self.waypoints_tree.index(item)
            
            # Remover waypoint
            del self.waypoints[index]
            self.refresh_waypoints_list()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover waypoint: {e}")
    
    def edit_waypoint(self):
        """Edita waypoint selecionado"""
        try:
            selection = self.waypoints_tree.selection()
            if not selection:
                messagebox.showerror("Erro", "Selecione um waypoint para editar!")
                return
            
            # Obter waypoint
            item = selection[0]
            index = self.waypoints_tree.index(item)
            waypoint = self.waypoints[index]
            
            # Preencher formulário
            self.waypoint_type_var.set(waypoint.type.value)
            self.waypoint_x_var.set(waypoint.x)
            self.waypoint_y_var.set(waypoint.y)
            self.waypoint_action_var.set(waypoint.action)
            self.waypoint_delay_var.set(waypoint.delay)
            
            # Remover waypoint atual (será re-adicionado com modificações)
            del self.waypoints[index]
            self.refresh_waypoints_list()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar waypoint: {e}")
    
    def clear_waypoints(self):
        """Limpa todos os waypoints"""
        try:
            if messagebox.askyesno("Confirmar", "Deseja remover todos os waypoints?"):
                self.waypoints.clear()
                self.refresh_waypoints_list()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao limpar waypoints: {e}")
    
    def toggle_recording(self):
        """Inicia/para gravação de waypoints"""
        try:
            if not self.recording:
                # Iniciar gravação
                self.recording = True
                self.record_button.config(text="Parar Gravação")
                self.record_status_label.config(text="Gravando...", foreground="red")
                messagebox.showinfo("Gravação", "Gravação iniciada! Use Ctrl+Click para adicionar waypoints.")
            else:
                # Parar gravação
                self.recording = False
                self.record_button.config(text="Iniciar Gravação")
                self.record_status_label.config(text="Parado", foreground="black")
                messagebox.showinfo("Gravação", "Gravação parada!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na gravação: {e}")
    
    def refresh_scripts_list(self):
        """Atualiza lista de scripts disponíveis"""
        try:
            self.scripts_listbox.delete(0, tk.END)
            
            scripts_dir = Path("scripts")
            scripts_dir.mkdir(exist_ok=True)
            
            for script_file in scripts_dir.glob("*.json"):
                self.scripts_listbox.insert(tk.END, script_file.stem)
                
        except Exception as e:
            pass  # Silencioso se diretório não existe
    
    def refresh_waypoints_list(self):
        """Atualiza lista de waypoints"""
        try:
            # Limpar tree
            for item in self.waypoints_tree.get_children():
                self.waypoints_tree.delete(item)
            
            # Adicionar waypoints
            for i, waypoint in enumerate(self.waypoints):
                self.waypoints_tree.insert("", "end", values=(
                    waypoint.type.value,
                    waypoint.x,
                    waypoint.y,
                    waypoint.action[:20]  # Truncar ação se muito longa
                ))
            
            # Atualizar contadores
            self.waypoint_label.config(text=f"0/{len(self.waypoints)}")
            
        except Exception as e:
            pass  # Silencioso em caso de erro
    
    def update_status(self):
        """Atualiza status do cavebot"""
        try:
            if hasattr(self.bot_manager.modules['cavebot'], 'get_status'):
                status = self.bot_manager.modules['cavebot'].get_status()
                
                # Atualizar labels
                if status['state'] == 'stopped':
                    self.status_label.config(text="Parado", foreground="red")
                elif status['state'] == 'walking':
                    self.status_label.config(text="Caminhando", foreground="green")
                elif status['state'] == 'fighting':
                    self.status_label.config(text="Lutando", foreground="orange")
                
                current_wp = status.get('current_waypoint', 0)
                total_wp = status.get('total_waypoints', 0)
                self.waypoint_label.config(text=f"{current_wp}/{total_wp}")
                
        except Exception:
            pass  # Silencioso se módulo não disponível
    
    def refresh(self):
        """Atualiza painel"""
        self.refresh_scripts_list()
        self.refresh_waypoints_list()
        self.update_status()