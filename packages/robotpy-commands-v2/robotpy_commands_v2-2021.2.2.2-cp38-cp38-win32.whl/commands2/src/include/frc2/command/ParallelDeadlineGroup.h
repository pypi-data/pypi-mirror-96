// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

#pragma once

#ifdef _WIN32
#pragma warning(push)
#pragma warning(disable : 4521)
#endif

#include <memory>
#include <utility>
#include <vector>

#include "frc2/command/CommandGroupBase.h"
#include "frc2/command/CommandHelper.h"

namespace frc2 {
/**
 * A CommandGroup that runs a set of commands in parallel, ending only when a
 * specific command (the "deadline") ends, interrupting all other commands that
 * are still running at that point.
 *
 * <p>As a rule, CommandGroups require the union of the requirements of their
 * component commands.
 */
class ParallelDeadlineGroup
    : public CommandGroupBase {
 public:
  /**
   * Creates a new ParallelDeadlineGroup.  The given commands (including the
   * deadline) will be executed simultaneously.  The CommandGroup will finish
   * when the deadline finishes, interrupting all other still-running commands.
   * If the CommandGroup is interrupted, only the commands still running will be
   * interrupted.
   *
   * @param deadline the command that determines when the group ends
   * @param commands the commands to be executed
   */
  ParallelDeadlineGroup(std::shared_ptr<Command> deadline,
                        std::vector<std::shared_ptr<Command>>&& commands);
  /**
   * Creates a new ParallelDeadlineGroup.  The given commands (including the
   * deadline) will be executed simultaneously.  The CommandGroup will finish
   * when the deadline finishes, interrupting all other still-running commands.
   * If the CommandGroup is interrupted, only the commands still running will be
   * interrupted.
   *
   * @param deadline the command that determines when the group ends
   * @param commands the commands to be executed
   */
  template <class T, class... Types,
            typename = std::enable_if_t<
                std::is_base_of_v<Command, std::remove_reference_t<T>>>,
            typename = std::enable_if_t<std::conjunction_v<
                std::is_base_of<Command, std::remove_reference_t<Types>>...>>>
  explicit ParallelDeadlineGroup(T&& deadline, Types&&... commands) {
    SetDeadline(std::make_shared<std::remove_reference_t<T>>(
        std::forward<T>(deadline)));
    AddCommands(std::forward<Types>(commands)...);
  }

  ParallelDeadlineGroup(ParallelDeadlineGroup&& other) = default;

  // No copy constructors for command groups
  ParallelDeadlineGroup(const ParallelDeadlineGroup&) = delete;

  // Prevent template expansion from emulating copy ctor
  ParallelDeadlineGroup(ParallelDeadlineGroup&) = delete;

  template <class... Types,
            typename = std::enable_if_t<std::conjunction_v<
                std::is_base_of<Command, std::remove_reference_t<Types>>...>>>
  void AddCommands(Types&&... commands) {
    std::vector<std::shared_ptr<Command>> foo;
    ((void)foo.emplace_back(std::make_shared<std::remove_reference_t<Types>>(
         std::forward<Types>(commands))),
     ...);
    AddCommands(std::move(foo));
  }

  void Initialize() override;

  void Execute() override;

  void End(bool interrupted) override;

  bool IsFinished() override;

  bool RunsWhenDisabled() const override;

 public:
  void AddCommands(std::vector<std::shared_ptr<Command>>&& commands) final;

 private:
  void SetDeadline(std::shared_ptr<Command> deadline);

  std::vector<std::pair<std::shared_ptr<Command>, bool>> m_commands;
  std::shared_ptr<Command> m_deadline;
  bool m_runWhenDisabled{true};
  bool m_finished{true};
};
}  // namespace frc2

#ifdef _WIN32
#pragma warning(pop)
#endif
